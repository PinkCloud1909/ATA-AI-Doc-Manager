from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import get_password_hash
from app.modules.iam.domain.models import Privilege, Role, User, UserRole
from app.modules.iam.domain.permissions import (
    ROLE_EDITOR,
    ROLE_REVIEWER,
    ROLE_VIEWER,
)
from app.shared.utils import utcnow

SEEDED_PRIVILEGES = [
    "GET:/health",
    "GET:/ready",
    "POST:/api/v1/auth/login",
    "POST:/api/v1/auth/register",
    "GET:/api/v1/auth/me",
    "POST:/api/v1/documents/upload",
    "GET:/api/v1/documents",
    "GET:/api/v1/documents/{document_id}",
    "PUT:/api/v1/documents/{document_id}",
    "DELETE:/api/v1/documents/{document_id}",
    "DELETE:/api/v1/documents/{document_id}/permanent",
    "POST:/api/v1/documents/{document_id}/new-version",
    "POST:/api/v1/documents/{document_id}/submit",
    "POST:/api/v1/documents/{document_id}/approve",
    "POST:/api/v1/documents/{document_id}/reject",
    "POST:/api/v1/documents/{document_id}/expire",
    "GET:/api/v1/approvals/pending",
    "POST:/api/v1/documents/{document_id}/reviews",
    "GET:/api/v1/documents/{document_id}/reviews",
    "POST:/api/v1/vectorization/{document_id}",
    "DELETE:/api/v1/vectorization/{document_id}",
    "GET:/api/v1/vectorization/{document_id}/status",
    "POST:/api/v1/vectorization/bulk",
    "POST:/qa/chat",
    # Admin management endpoints
    "POST:/api/v1/admin/users",
    "GET:/api/v1/admin/users",
    "GET:/api/v1/admin/users/{user_id}",
    "POST:/api/v1/admin/users/{user_id}/roles",
    "DELETE:/api/v1/admin/users/{user_id}/roles/{role_name}",
    "GET:/api/v1/admin/roles",
]
DEFAULT_USER_PRIVILEGES = ["GET:/api/v1/auth/me"]

# --- Per-role privilege definitions ---

VIEWER_PRIVILEGES = [
    "GET:/api/v1/auth/me",
    "GET:/api/v1/documents",
    "GET:/api/v1/documents/{document_id}",
]

EDITOR_PRIVILEGES = [
    "GET:/api/v1/auth/me",
    "GET:/api/v1/documents",
    "GET:/api/v1/documents/{document_id}",
    "POST:/api/v1/documents/upload",
    "PUT:/api/v1/documents/{document_id}",
    "POST:/api/v1/documents/{document_id}/new-version",
    "POST:/api/v1/documents/{document_id}/submit",
]

REVIEWER_PRIVILEGES = [
    "GET:/api/v1/auth/me",
    "GET:/api/v1/documents",
    "GET:/api/v1/documents/{document_id}",
    "GET:/api/v1/approvals/pending",
    "POST:/api/v1/documents/{document_id}/approve",
    "POST:/api/v1/documents/{document_id}/reject",
    "POST:/api/v1/documents/{document_id}/reviews",
    "GET:/api/v1/documents/{document_id}/reviews",
    "POST:/api/v1/documents/{document_id}/expire",
]

ROLE_PRIVILEGES: dict[str, list[str]] = {
    ROLE_VIEWER: VIEWER_PRIVILEGES,
    ROLE_EDITOR: EDITOR_PRIVILEGES,
    ROLE_REVIEWER: REVIEWER_PRIVILEGES,
}


def _seed_role_with_privileges(
    session: Session,
    role_name: str,
    description: str,
    privilege_endpoints: list[str],
) -> Role:
    """Create or update a role and ensure all its privileges exist (idempotent)."""
    role = session.execute(
        select(Role).where(Role.role_name == role_name)
    ).scalar_one_or_none()
    if role is None:
        role = Role(role_name=role_name, description=description)
        session.add(role)
        session.flush()

    existing = {
        p.api_endpoint: p
        for p in session.execute(
            select(Privilege).where(Privilege.role_id == role.id)
        ).scalars()
    }
    for endpoint in privilege_endpoints:
        priv = existing.get(endpoint)
        if priv is None:
            session.add(
                Privilege(
                    role_id=role.id,
                    api_endpoint=endpoint,
                    is_allowed=True,
                )
            )
        elif priv.is_allowed is not True:
            priv.is_allowed = True

    return role


def seed_iam_data(
    session: Session,
    settings: Settings | None = None,
) -> dict[str, str]:
    settings = settings or get_settings()

    # --- Admin role + user ---
    admin_role = _seed_role_with_privileges(
        session,
        role_name=settings.default_admin_role_name,
        description="Default administrator role",
        privilege_endpoints=SEEDED_PRIVILEGES,
    )

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
            UserRole.role_id == admin_role.id,
        )
    ).scalar_one_or_none()
    if assignment is None:
        session.add(
            UserRole(
                user_id=user.id,
                role_id=admin_role.id,
                assigned_by=user.id,
                assigned_at=utcnow(),
            )
        )

    # --- Default self-service user role ---
    _seed_role_with_privileges(
        session,
        role_name=settings.default_user_role_name,
        description="Default self-service user role",
        privilege_endpoints=DEFAULT_USER_PRIVILEGES,
    )

    # --- Application roles: viewer, editor, reviewer ---
    for role_name, endpoints in ROLE_PRIVILEGES.items():
        _seed_role_with_privileges(
            session,
            role_name=role_name,
            description=f"{role_name.capitalize()} role",
            privilege_endpoints=endpoints,
        )

    session.flush()
    return {
        "admin_username": settings.default_admin_username,
        "admin_role": settings.default_admin_role_name,
    }

