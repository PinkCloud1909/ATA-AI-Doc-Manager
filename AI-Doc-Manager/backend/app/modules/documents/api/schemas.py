from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.enums import DocumentType, Status


class RejectRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=2000)


class DocumentCreateRequest(BaseModel):
    document_type: DocumentType
    file_link: str = Field(min_length=1)
    title: str | None = Field(default=None, max_length=500)
    description: str | None = None
    original_filename: str | None = Field(default=None, max_length=500)
    file_size: int | None = Field(default=None, ge=0)
    content_type: str | None = Field(default=None, max_length=200)


class DocumentUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    document_type: DocumentType | None = None


class SignedUploadUrlRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=500)
    content_type: str = Field(default="application/octet-stream", max_length=200)


class SignedUploadUrlResponse(BaseModel):
    signed_url: str
    gcs_path: str


class ConfirmUploadRequest(BaseModel):
    gcs_path: str = Field(min_length=1)
    original_filename: str = Field(min_length=1, max_length=500)
    content_type: str = Field(default="application/octet-stream", max_length=200)
    size_bytes: int = Field(default=0, ge=0)
    document_type: DocumentType
    document_group_id: UUID | None = None
    title: str | None = Field(default=None, max_length=500)
    description: str | None = None


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


class DocumentListResponse(BaseModel):
    id: UUID
    document_id: UUID
    document_group_id: UUID
    version: int
    document_type: DocumentType
    status: Status
    title: str
    description: str | None = None
    file_link: str | None = None
    original_filename: str
    file_size: int | None = None
    size_bytes: int | None = None
    content_type: str | None = None
    is_vectorized: bool | None = None
    vertex_index_id: str | None = None
    created_by: UUID | None = None
    created_by_name: str | None = None
    created_at: datetime | None = None
    avg_grade: float | None = None


class DocumentDetailResponse(BaseModel):
    id: UUID
    document_id: UUID
    document_group_id: UUID
    version: int
    document_type: DocumentType
    status: Status
    title: str
    description: str | None = None
    file_link: str
    original_filename: str
    file_size: int | None = None
    size_bytes: int | None = None
    content_type: str | None = None
    is_vectorized: bool | None = None
    vertex_index_id: str | None = None
    download_url: str | None = None
    created_by: UUID | None = None
    created_by_name: str | None = None
    created_at: datetime | None = None
    modified_by: UUID | None = None
    modified_date: datetime | None = None
    reviews: list[dict] = Field(default_factory=list)
    avg_grade: float | None = None


class PaginatedDocumentsResponse(BaseModel):
    items: list[DocumentListResponse]
    total: int
    page: int
    page_size: int


class VersionHistoryItem(BaseModel):
    id: UUID
    version: int
    status: Status
    created_at: datetime | None = None
    created_by: UUID | None = None


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
