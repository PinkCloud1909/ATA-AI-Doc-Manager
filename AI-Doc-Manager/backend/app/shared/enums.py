from enum import Enum


class DocumentType(str, Enum):
    """Document category — used for filtering and classification."""

    POLICY = "policy"
    MANUAL = "manual"
    REPORT = "report"
    OTHER = "other"


class Status(str, Enum):
    """Document lifecycle status.

    Transitions are enforced by the application service layer:

    - **DRAFT** → PENDING_REVIEW (on submit)
    - **PENDING_REVIEW** → APPROVED | REJECTED (on reviewer action)
    - **APPROVED** → EXPIRED (on expiry)
    - Any → ARCHIVED (on soft-delete)
    """

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ACTIVE = "active"
    ARCHIVED = "archived"


def enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]
