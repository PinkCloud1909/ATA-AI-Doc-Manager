import logging
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
<<<<<<< Updated upstream
from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError, ValidationError
=======
from app.core.exceptions import ConflictError, UnauthorizedError, ValidationError
>>>>>>> Stashed changes
from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.iam.domain.models import Privilege, Role, User, UserRole
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.iam.domain.password_policy import validate_password_policy
from app.modules.iam.infrastructure.repositories import (
    get_privilege_by_role_and_endpoint,
    get_role_by_name,
    get_user_by_email,
    get_user_by_firebase_uid,
    get_user_by_id,
    get_user_by_username,
)
from app.shared.utils import utcnow

logger = logging.getLogger(__name__)

<<<<<<< Updated upstream
DEFAULT_USER_PERMISSIONS = [
    "GET:/api/v1/auth/me",
    "POST:/api/v1/auth/logout",
    "POST:/api/v1/auth/password-changed",
    "GET:/api/v1/documents",
    "GET:/api/v1/documents/{document_id}",
    "GET:/api/v1/documents/{document_id}/download-url",
    "GET:/api/v1/documents/{document_id}/download",
    "GET:/api/v1/documents/{document_id}/versions",
    "GET:/api/v1/documents/{document_id}/reviews",
    "POST:/api/v1/qa/chat",
]
=======
DEFAULT_SELF_SERVICE_PERMISSIONS = (
    "GET:/api/v1/auth/me",
    "POST:/api/v1/auth/change-password",
)
>>>>>>> Stashed changes


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


def issue_access_token(session: Session, username: str, password: str) -> tuple[str, int]:
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

<<<<<<< Updated upstream
    for permission in DEFAULT_USER_PERMISSIONS:
=======
    for permission in DEFAULT_SELF_SERVICE_PERMISSIONS:
>>>>>>> Stashed changes
        privilege = get_privilege_by_role_and_endpoint(
            session,
            role_id=role.id,
            api_endpoint=permission,
        )
        if privilege is None:
            session.add(
                Privilege(
                    role_id=role.id,
                    api_endpoint=permission,
                    is_allowed=True,
                )
            )
<<<<<<< Updated upstream
            session.flush()
        elif privilege.is_allowed is not True:
            privilege.is_allowed = True
=======
        elif privilege.is_allowed is not True:
            privilege.is_allowed = True
    session.flush()
>>>>>>> Stashed changes

    return role


def list_roles(session: Session) -> list[Role]:
    stmt = select(Role).options(joinedload(Role.privileges)).order_by(Role.role_name)
    return list(session.execute(stmt).unique().scalars().all())


def list_users(session: Session) -> list[User]:
    stmt = (
        select(User)
        .options(
            joinedload(User.user_roles)
            .joinedload(UserRole.role)
            .joinedload(Role.privileges)
        )
        .order_by(User.username)
    )
    return list(session.execute(stmt).unique().scalars().all())


def _load_roles_by_name(session: Session, role_names: list[str]) -> list[Role]:
    normalized = sorted({name.strip().lower() for name in role_names if name.strip()})
    if not normalized:
        raise ValidationError("At least one role is required")

    roles = list(
        session.execute(select(Role).where(Role.role_name.in_(normalized)))
        .scalars()
        .all()
    )
    found = {role.role_name for role in roles}
    missing = [role_name for role_name in normalized if role_name not in found]
    if missing:
        raise ValidationError(f"Unknown role(s): {', '.join(missing)}")
    return roles


def assign_roles_to_user(
    session: Session,
    *,
    user_id: UUID,
    role_names: list[str],
    assigned_by: UUID | None,
) -> User:
    user = get_user_by_id(session, user_id)
    if user is None:
        raise NotFoundError("User not found")

    roles = _load_roles_by_name(session, role_names)
    session.execute(delete(UserRole).where(UserRole.user_id == user_id))
    now = utcnow()
    for role in roles:
        session.add(
            UserRole(
                user_id=user_id,
                role_id=role.id,
                assigned_by=assigned_by,
                assigned_at=now,
            )
        )
    session.commit()
    session.expire_all()

    refreshed_user = get_user_by_id(session, user_id)
    if refreshed_user is None:
        raise NotFoundError("User not found")
    return refreshed_user


def create_user(
    session: Session,
    *,
    username: str,
    password: str,
    role_names: list[str],
    created_by: UUID | None,
) -> User:
    if get_user_by_username(session, username) is not None:
        raise ConflictError("Username already exists")

    roles = _load_roles_by_name(session, role_names or ["viewer"])
    user = User(
        username=username,
        password_hash=get_password_hash(password),
        last_password_changed=utcnow(),
    )
    session.add(user)
    try:
        session.flush()
        now = utcnow()
        for role in roles:
            session.add(
                UserRole(
                    user_id=user.id,
                    role_id=role.id,
                    assigned_by=created_by,
                    assigned_at=now,
                )
            )
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise ConflictError("Username already exists") from exc

    refreshed_user = get_user_by_id(session, user.id)
    if refreshed_user is None:
        raise NotFoundError("User not found")
    return refreshed_user


def register_user(session: Session, username: str, password: str) -> AuthenticatedUser:
    logger.info("register_attempt", extra={"username": username})
    validate_password_policy(password)
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
        logger.warning("auth_failure", extra={"reason": "user_not_found", "user_id": str(user_id)})
        raise UnauthorizedError("Invalid authentication credentials")

    return build_principal(user)


def get_or_create_firebase_user(
    session: Session,
<<<<<<< Updated upstream
    firebase_uid: str,
    email: str | None,
    display_name: str | None,
) -> User:
    user = get_user_by_firebase_uid(session, firebase_uid)
    if user:
        return user

    fallback_username = display_name or email or f"user-{firebase_uid[:8]}"
    existing_by_email = get_user_by_email(session, email) if email else None
    if existing_by_email:
        existing_by_email.firebase_uid = firebase_uid
        session.flush()
        return existing_by_email

    default_role = _ensure_default_user_role(session)
=======
    *,
    username: str,
    password: str,
    role_names: list[str],
    assigned_by: UUID | None = None,
) -> AuthenticatedUser:
    """Create a new user and optionally assign roles."""
    logger.info("admin_create_user_attempt", extra={"username": username})
    validate_password_policy(password)
    if get_user_by_username(session, username) is not None:
        raise ConflictError("Username already exists")

    if not role_names:
        role_names = [_ensure_default_user_role(session).role_name]

>>>>>>> Stashed changes
    user = User(
        username=fallback_username,
        email=email,
        firebase_uid=firebase_uid,
        password_hash=get_password_hash(firebase_uid),
        last_password_changed=utcnow(),
    )
    session.add(user)
<<<<<<< Updated upstream
    session.flush()
=======

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
        principal = build_principal(user)
        items.append(
            {
                "id": user.id,
                "username": user.username,
                "roles": principal.roles,
                "permissions": sorted(principal.permissions),
            }
        )
    return items, total


def get_user_detail(session: Session, user_id: UUID) -> dict:
    """Return user detail with role names."""
    user = get_user_by_id(session, user_id)
    if user is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("User not found")
    principal = build_principal(user)
    return {
        "id": user.id,
        "username": user.username,
        "roles": principal.roles,
        "permissions": sorted(principal.permissions),
    }


def change_password(
    session: Session,
    *,
    user_id: UUID,
    current_password: str,
    new_password: str,
) -> None:
    """Change the authenticated user's password after verifying the old one."""
    user = get_user_by_id(session, user_id)
    if user is None:
        raise UnauthorizedError("Invalid authentication credentials")
    if not verify_password(current_password, user.password_hash):
        raise ValidationError("Current password is incorrect")
    if current_password == new_password:
        raise ValidationError("New password must be different from current password")

    validate_password_policy(new_password)
    user.password_hash = get_password_hash(new_password)
    user.last_password_changed = utcnow()
    session.commit()
    logger.info("password_changed", extra={"user_id": str(user_id)})


def reset_user_password(
    session: Session,
    *,
    user_id: UUID,
    new_password: str,
) -> None:
    """Set a new password for a user without requiring their current password."""
    user = get_user_by_id(session, user_id)
    if user is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("User not found")

    validate_password_policy(new_password)
    user.password_hash = get_password_hash(new_password)
    user.last_password_changed = utcnow()
    session.commit()
    logger.info("password_reset_by_admin", extra={"user_id": str(user_id)})


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

>>>>>>> Stashed changes
    session.add(
        UserRole(
            user_id=user.id,
            role_id=default_role.id,
            assigned_by=None,
            assigned_at=utcnow(),
        )
    )
<<<<<<< Updated upstream
    session.flush()
    return user
=======
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
        {
            "id": role.id,
            "role_name": role.role_name,
            "description": role.description,
            "permissions": sorted(
                privilege.api_endpoint
                for privilege in role.privileges
                if privilege.api_endpoint and privilege.is_allowed
            ),
        }
        for role in roles
    ]
>>>>>>> Stashed changes
