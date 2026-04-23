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
        logger.warning("auth_failure", extra={"reason": "user_not_found", "user_id": str(user_id)})
        raise UnauthorizedError("Invalid authentication credentials")

    return build_principal(user)
