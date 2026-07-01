from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import get_password_hash
from app.modules.iam.domain.models import Privilege, Role, User, UserRole
from app.shared.utils import utcnow

SELF_SERVICE_PRIVILEGES = [
    "GET:/api/v1/auth/me",
    "POST:/api/v1/auth/logout",
    "POST:/api/v1/auth/password-changed",
]

DOCUMENT_READ_PRIVILEGES = [
    "GET:/api/v1/documents",
    "GET:/api/v1/documents/{document_id}",
    "GET:/api/v1/documents/{document_id}/download-url",
    "GET:/api/v1/documents/{document_id}/download",
    "GET:/api/v1/documents/{document_id}/versions",
    "GET:/api/v1/documents/{document_id}/reviews",
    "POST:/api/v1/qa/chat",
    "GET:/api/v1/reports/summary",
    "GET:/api/v1/reports/approval-rate",
    "GET:/api/v1/reports/avg-grade",
    "GET:/api/v1/reports/activity",
]

EDITOR_PRIVILEGES = [
    *SELF_SERVICE_PRIVILEGES,
    *DOCUMENT_READ_PRIVILEGES,
    "POST:/api/v1/documents",
    "POST:/api/v1/documents/upload",
    "POST:/api/v1/documents/signed-upload-url",
    "POST:/api/v1/documents/confirm-upload",
    "PUT:/api/v1/documents/{document_id}",
    "POST:/api/v1/documents/{document_id}/new-version",
    "POST:/api/v1/documents/{document_id}/submit",
    "POST:/api/v1/generate/runbook",
]

REVIEWER_PRIVILEGES = [
    *SELF_SERVICE_PRIVILEGES,
    *DOCUMENT_READ_PRIVILEGES,
    "POST:/api/v1/documents/{document_id}/approve",
    "POST:/api/v1/documents/{document_id}/reject",
    "POST:/api/v1/documents/{document_id}/expire",
    "POST:/api/v1/documents/{document_id}/reviews",
    "GET:/api/v1/reviews",
    "GET:/api/v1/approvals/pending",
    "POST:/api/v1/approvals/{document_id}/approve",
    "POST:/api/v1/approvals/{document_id}/reject",
    "GET:/api/v1/approvals/approved",
    "GET:/api/v1/approvals/rejected",
]

VIEWER_PRIVILEGES = [
    *SELF_SERVICE_PRIVILEGES,
    *DOCUMENT_READ_PRIVILEGES,
]

ADMIN_PRIVILEGES = [
    "GET:/health",
    "GET:/ready",
    "POST:/api/v1/auth/login",
    "POST:/api/v1/auth/register",
    *EDITOR_PRIVILEGES,
    *REVIEWER_PRIVILEGES,
    "DELETE:/api/v1/documents/{document_id}",
    "DELETE:/api/v1/documents/{document_id}/permanent",
    "GET:/api/v1/admin/roles",
    "GET:/api/v1/admin/users",
    "POST:/api/v1/admin/users",
    "PUT:/api/v1/admin/users/{user_id}/roles",
]

ROLE_PRIVILEGES = {
    "admin": ADMIN_PRIVILEGES,
    "viewer": VIEWER_PRIVILEGES,
    "editor": EDITOR_PRIVILEGES,
    "reviewer": REVIEWER_PRIVILEGES,
}


def _dedupe(values: list[str]) -> list[str]:
    return sorted(set(values))


SEEDED_PRIVILEGES = _dedupe(ADMIN_PRIVILEGES)
DEFAULT_USER_PRIVILEGES = VIEWER_PRIVILEGES


def _ensure_role(
    session: Session,
    role_name: str,
    description: str,
    privileges: list[str],
) -> Role:
    role = session.execute(
        select(Role).where(Role.role_name == role_name)
    ).scalar_one_or_none()
    if role is None:
        role = Role(role_name=role_name, description=description)
        session.add(role)
        session.flush()
    else:
        role.description = description

    existing_privileges = {
        privilege.api_endpoint: privilege
        for privilege in session.execute(
            select(Privilege).where(Privilege.role_id == role.id)
        ).scalars()
    }
    for api_endpoint in _dedupe(privileges):
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
    return role


def seed_iam_data(
    session: Session,
    settings: Settings | None = None,
) -> dict[str, str]:
    settings = settings or get_settings()

    role = _ensure_role(
        session,
        settings.default_admin_role_name,
        "Full administrator role",
        ADMIN_PRIVILEGES,
    )

    _ensure_role(
        session,
        "viewer",
        "List approved and expired documents",
        VIEWER_PRIVILEGES,
    )
    _ensure_role(
        session,
        "editor",
        "Create, update, and submit document versions",
        EDITOR_PRIVILEGES,
    )
    _ensure_role(
        session,
        "reviewer",
        "Review documents and manage approval decisions",
        REVIEWER_PRIVILEGES,
    )
    _ensure_role(
        session,
        settings.default_user_role_name,
        "Default viewer-compatible user role",
        DEFAULT_USER_PRIVILEGES,
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

    session.flush()
    return {
        "admin_username": settings.default_admin_username,
        "admin_role": settings.default_admin_role_name,
    }
