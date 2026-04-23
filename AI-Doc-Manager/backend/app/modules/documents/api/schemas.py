from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.enums import DocumentType, Status


class RejectRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=2000)


class DocumentActionResponse(BaseModel):
    document_id: UUID
    document_group_id: UUID
    version: int
    document_type: DocumentType
    status: Status
    submitted_by: UUID | None = None
    submitted_at: datetime | None = None
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    rejected_by: UUID | None = None
    rejected_reason: str | None = None
    rejected_at: datetime | None = None


class ApprovalQueueItem(BaseModel):
    document_id: UUID
    document_group_id: UUID
    version: int
    document_type: DocumentType
    status: Status
    created_by: UUID | None = None
    created_at: datetime | None = None
    submitted_by: UUID | None = None
    submitted_at: datetime | None = None
