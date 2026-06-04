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


# --- Document Management schemas ---


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    document_group_id: UUID
    version: int
    title: str
    original_filename: str
    document_type: DocumentType
    status: Status
    file_size: int | None = None
    content_type: str | None = None
    created_by: UUID | None = None
    created_at: datetime | None = None


class DocumentDetailResponse(BaseModel):
    document_id: UUID
    document_group_id: UUID
    version: int
    title: str
    description: str | None = None
    original_filename: str
    document_type: DocumentType
    status: Status
    file_size: int | None = None
    content_type: str | None = None
    download_url: str
    is_vectorized: bool | None = None
    created_by: UUID | None = None
    created_at: datetime | None = None
    modified_by: UUID | None = None
    modified_date: datetime | None = None
    submitted_by: UUID | None = None
    submitted_at: datetime | None = None
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    rejected_by: UUID | None = None
    rejected_reason: str | None = None
    rejected_at: datetime | None = None


class DocumentListItem(BaseModel):
    document_id: UUID
    document_group_id: UUID
    version: int
    title: str
    original_filename: str
    document_type: DocumentType
    status: Status
    file_size: int | None = None
    content_type: str | None = None
    created_by: UUID | None = None
    created_at: datetime | None = None


class DocumentListResponse(BaseModel):
    items: list[DocumentListItem]
    total: int
    page: int
    page_size: int


class DocumentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    document_type: DocumentType | None = None


class DocumentDeleteResponse(BaseModel):
    detail: str
    document_id: UUID
