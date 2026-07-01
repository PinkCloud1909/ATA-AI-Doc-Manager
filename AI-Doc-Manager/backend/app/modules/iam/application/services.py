import logging
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.iam.domain.models import Privilege, Role, User, UserRole
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.iam.infrastructure.repositories import (
    get_privilege_by_role_and_endpoint,
    get_role_by_name,
    get_user_by_id,
    get_user_by_username,
)
from app.shared.utils import utcnow

logger = logging.getLogger(__name__)

DEFAULT_SELF_SERVICE_PERMISSION = "GET:/api/v1/auth/me"


def build_principal(user: User) -> AuthenticatedUser:
    roles = []
    permissions: set[str] = set()
    for user_role in user.user_roles:
        role = user_role.role
        if role is None:
            continue
        roles.append(role.role_name)
        for privilege in role.privileges:
            if privilege.api_endpoint and privilege.is_allowed:
                permissions.add(privilege.api_endpoint)

    return AuthenticatedUser(
        id=user.id,
        username=user.username,
        roles=sorted(set(roles)),
        permissions=permissions,
    )


def authenticate_user(session: Session, username: str, password: str) -> User:
    logger.info("login_attempt", extra={"username": username})
    user = get_user_by_username(session, username)
    if user is None or not verify_password(password, user.password_hash):
        logger.warning("login_failure", extra={"username": username})
        raise UnauthorizedError("Invalid username or password")

    logger.info("login_success", extra={"user_id": str(user.id), "username": username})
    return user


def issue_access_token(
    session: Session, username: str, password: str
) -> tuple[str, int]:
    user = authenticate_user(session, username=username, password=password)
    return create_access_token(subject=str(user.id), username=user.username)


def _ensure_default_user_role(session: Session) -> Role:
    settings = get_settings()
    role = get_role_by_name(session, settings.default_user_role_name)
    if role is None:
        role = Role(
            role_name=settings.default_user_role_name,
            description="Default self-service user role",
        )
        session.add(role)
        session.flush()

    privilege = get_privilege_by_role_and_endpoint(
        session,
        role_id=role.id,
        api_endpoint=DEFAULT_SELF_SERVICE_PERMISSION,
    )
    if privilege is None:
        session.add(
            Privilege(
                role_id=role.id,
                api_endpoint=DEFAULT_SELF_SERVICE_PERMISSION,
                is_allowed=True,
            )
        )
        session.flush()
    elif privilege.is_allowed is not True:
        privilege.is_allowed = True

    return role


def register_user(session: Session, username: str, password: str) -> AuthenticatedUser:
    logger.info("register_attempt", extra={"username": username})
    if get_user_by_username(session, username) is not None:
        logger.warning("register_conflict", extra={"username": username})
        raise ConflictError("Username already exists")

    default_role = _ensure_default_user_role(session)
    user = User(
        username=username,
        password_hash=get_password_hash(password),
        last_password_changed=utcnow(),
    )
    session.add(user)

    try:
        session.flush()
        session.add(
            UserRole(
                user_id=user.id,
                role_id=default_role.id,
                assigned_by=None,
                assigned_at=utcnow(),
            )
        )
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        logger.warning("register_conflict", extra={"username": username})
        raise ConflictError("Username already exists") from exc

    logger.info(
        "register_success",
        extra={
            "user_id": str(user.id),
            "username": username,
            "role_name": default_role.role_name,
        },
    )
    return load_principal(session, user.id)


def load_principal(session: Session, user_id: UUID) -> AuthenticatedUser:
    user = get_user_by_id(session, user_id)
    if user is None:
        logger.warning(
            "auth_failure", extra={"reason": "user_not_found", "user_id": str(user_id)}
        )
        raise UnauthorizedError("Invalid authentication credentials")

    return build_principal(user)


# ---------------------------------------------------------------------------
# Admin management functions
# ---------------------------------------------------------------------------


def create_user_with_roles(
    session: Session,
    *,
    username: str,
    password: str,
    role_names: list[str],
    assigned_by: UUID | None = None,
) -> AuthenticatedUser:
    """Create a new user and optionally assign roles."""
    logger.info("admin_create_user_attempt", extra={"username": username})
    if get_user_by_username(session, username) is not None:
        raise ConflictError("Username already exists")

    user = User(
        username=username,
        password_hash=get_password_hash(password),
        last_password_changed=utcnow(),
    )
    session.add(user)

    try:
        session.flush()

        for role_name in role_names:
            role = get_role_by_name(session, role_name)
            if role is None:
                from app.core.exceptions import NotFoundError

                raise NotFoundError(f"Role '{role_name}' not found")
            session.add(
                UserRole(
                    user_id=user.id,
                    role_id=role.id,
                    assigned_by=assigned_by,
                    assigned_at=utcnow(),
                )
            )

        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise ConflictError("Username already exists") from exc

    logger.info(
        "admin_create_user_success",
        extra={"user_id": str(user.id), "username": username, "roles": role_names},
    )
    return load_principal(session, user.id)


def list_all_users(
    session: Session,
    *,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[dict], int]:
    """Return a paginated list of users with their role names."""
    from app.modules.iam.infrastructure.repositories import list_users

    users, total = list_users(session, page=page, page_size=page_size)
    items = []
    for user in users:
        role_names = sorted({ur.role.role_name for ur in user.user_roles if ur.role})
        items.append(
            {
                "id": user.id,
                "username": user.username,
                "roles": role_names,
            }
        )
    return items, total


def get_user_detail(session: Session, user_id: UUID) -> dict:
    """Return user detail with role names."""
    user = get_user_by_id(session, user_id)
    if user is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("User not found")
    role_names = sorted({ur.role.role_name for ur in user.user_roles if ur.role})
    return {
        "id": user.id,
        "username": user.username,
        "roles": role_names,
    }


def assign_role_to_user(
    session: Session,
    *,
    user_id: UUID,
    role_name: str,
    assigned_by: UUID | None = None,
) -> dict:
    """Assign a role to a user. Returns updated user detail."""
    user = get_user_by_id(session, user_id)
    if user is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("User not found")

    role = get_role_by_name(session, role_name)
    if role is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError(f"Role '{role_name}' not found")

    from app.modules.iam.infrastructure.repositories import get_user_role

    existing = get_user_role(session, user_id=user.id, role_id=role.id)
    if existing is not None:
        raise ConflictError(f"User already has role '{role_name}'")

    session.add(
        UserRole(
            user_id=user.id,
            role_id=role.id,
            assigned_by=assigned_by,
            assigned_at=utcnow(),
        )
    )
    session.commit()

    logger.info(
        "admin_assign_role",
        extra={"user_id": str(user.id), "role": role_name},
    )
    return get_user_detail(session, user.id)


def remove_role_from_user(
    session: Session,
    *,
    user_id: UUID,
    role_name: str,
) -> dict:
    """Remove a role from a user. Returns updated user detail."""
    user = get_user_by_id(session, user_id)
    if user is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("User not found")

    role = get_role_by_name(session, role_name)
    if role is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError(f"Role '{role_name}' not found")

    from app.modules.iam.infrastructure.repositories import get_user_role

    assignment = get_user_role(session, user_id=user.id, role_id=role.id)
    if assignment is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError(f"User does not have role '{role_name}'")

    session.delete(assignment)
    session.commit()

    logger.info(
        "admin_remove_role",
        extra={"user_id": str(user.id), "role": role_name},
    )
    return get_user_detail(session, user.id)


def list_all_roles(session: Session) -> list[dict]:
    """Return all roles."""
    from app.modules.iam.infrastructure.repositories import list_roles

    roles = list_roles(session)
    return [
        {"id": role.id, "role_name": role.role_name, "description": role.description}
        for role in roles
    ]
