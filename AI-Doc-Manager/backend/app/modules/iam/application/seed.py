from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import get_password_hash
from app.modules.iam.domain.models import Privilege, Role, User, UserRole
from app.shared.utils import utcnow

SEEDED_PRIVILEGES = [
    "GET:/health",
    "GET:/ready",
    "POST:/api/v1/auth/login",
    "POST:/api/v1/auth/register",
    "GET:/api/v1/auth/me",
    "POST:/api/v1/documents/{document_id}/submit",
    "POST:/api/v1/documents/{document_id}/approve",
    "POST:/api/v1/documents/{document_id}/reject",
    "GET:/api/v1/approvals/pending",
    "POST:/api/v1/documents/{document_id}/reviews",
    "GET:/api/v1/documents/{document_id}/reviews",
]
DEFAULT_USER_PRIVILEGES = ["GET:/api/v1/auth/me"]


def seed_iam_data(
    session: Session,
    settings: Settings | None = None,
) -> dict[str, str]:
    settings = settings or get_settings()

    role = session.execute(
        select(Role).where(Role.role_name == settings.default_admin_role_name)
    ).scalar_one_or_none()
    if role is None:
        role = Role(
            role_name=settings.default_admin_role_name,
            description="Default administrator role",
        )
        session.add(role)
        session.flush()

    user = session.execute(
        select(User).where(User.username == settings.default_admin_username)
    ).scalar_one_or_none()
    if user is None:
        user = User(
            username=settings.default_admin_username,
            password_hash=get_password_hash(settings.default_admin_password),
            last_password_changed=utcnow(),
        )
        session.add(user)
        session.flush()

    assignment = session.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
    ).scalar_one_or_none()
    if assignment is None:
        session.add(
            UserRole(
                user_id=user.id,
                role_id=role.id,
                assigned_by=user.id,
                assigned_at=utcnow(),
            )
        )

    existing_privileges = {
        privilege.api_endpoint: privilege
        for privilege in session.execute(
            select(Privilege).where(Privilege.role_id == role.id)
        ).scalars()
    }
    for api_endpoint in SEEDED_PRIVILEGES:
        privilege = existing_privileges.get(api_endpoint)
        if privilege is None:
            session.add(
                Privilege(
                    role_id=role.id,
                    api_endpoint=api_endpoint,
                    is_allowed=True,
                )
            )
        elif privilege.is_allowed is not True:
            privilege.is_allowed = True

    default_user_role = session.execute(
        select(Role).where(Role.role_name == settings.default_user_role_name)
    ).scalar_one_or_none()
    if default_user_role is None:
        default_user_role = Role(
            role_name=settings.default_user_role_name,
            description="Default self-service user role",
        )
        session.add(default_user_role)
        session.flush()

    default_user_privileges = {
        privilege.api_endpoint: privilege
        for privilege in session.execute(
            select(Privilege).where(Privilege.role_id == default_user_role.id)
        ).scalars()
    }
    for api_endpoint in DEFAULT_USER_PRIVILEGES:
        privilege = default_user_privileges.get(api_endpoint)
        if privilege is None:
            session.add(
                Privilege(
                    role_id=default_user_role.id,
                    api_endpoint=api_endpoint,
                    is_allowed=True,
                )
            )
        elif privilege.is_allowed is not True:
            privilege.is_allowed = True

    session.flush()
    return {
        "admin_username": settings.default_admin_username,
        "admin_role": settings.default_admin_role_name,
    }
