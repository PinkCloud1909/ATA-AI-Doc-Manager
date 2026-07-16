"""Centralized permission & role constants for the IAM module."""

from app.shared.enums import Status


# --- Role names ---
ROLE_ADMIN = "admin"
ROLE_VIEWER = "viewer"
ROLE_EDITOR = "editor"
ROLE_REVIEWER = "reviewer"

ALL_APPLICATION_ROLES = [ROLE_VIEWER, ROLE_EDITOR, ROLE_REVIEWER]

# --- Status visibility per role ---
# Defines which document statuses each role is allowed to see when listing documents.
ROLE_STATUS_ACCESS: dict[str, set[Status]] = {
    ROLE_VIEWER: {Status.APPROVED, Status.EXPIRED},
    ROLE_EDITOR: {
        Status.DRAFT,
        Status.PENDING_REVIEW,
        Status.APPROVED,
        Status.REJECTED,
        Status.EXPIRED,
    },
    ROLE_REVIEWER: {
        Status.PENDING_REVIEW,
        Status.APPROVED,
        Status.REJECTED,
        Status.EXPIRED,
    },
    ROLE_ADMIN: set(Status),  # Admin sees all statuses
}


def get_allowed_statuses(roles: list[str]) -> set[Status]:
    """Return the union of visible statuses for a list of roles."""
    allowed: set[Status] = set()
    for role in roles:
        allowed |= ROLE_STATUS_ACCESS.get(role, set())
    return allowed
