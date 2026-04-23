from enum import Enum


class DocumentType(str, Enum):
    POLICY = "policy"
    MANUAL = "manual"
    REPORT = "report"
    OTHER = "other"


class Status(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ACTIVE = "active"
    ARCHIVED = "archived"


def enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]
