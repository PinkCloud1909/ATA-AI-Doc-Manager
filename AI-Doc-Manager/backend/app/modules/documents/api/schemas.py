from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.enums import DocumentType, Status


class RejectRequest(BaseModel):
    """Payload to reject a submitted document with a reason."""

    reason: str = Field(
        min_length=1,
        max_length=2000,
        description="Explanation for the rejection (1–2000 characters)",
        examples=["The policy references an outdated compliance standard (SOC 2 2019). Please update to SOC 2 2024."],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "reason": "The policy references an outdated compliance standard. Please update."
            }
        }
    }


class DocumentActionResponse(BaseModel):
    """Result of a workflow action (submit, approve, reject, expire)."""

    document_id: UUID = Field(
        description="Unique document identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    document_group_id: UUID = Field(
        description="Group identifier linking all versions of the same logical document",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    version: int = Field(
        description="Monotonically increasing version number (1-based)",
        examples=[3],
    )
    document_type: DocumentType = Field(
        description="Document category: policy, manual, report, or other",
    )
    status: Status = Field(
        description="Current lifecycle status after the action",
    )
    submitted_by: UUID | None = Field(
        default=None,
        description="UUID of the user who submitted the document for review",
    )
    submitted_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was submitted (UTC)",
    )
    approved_by: UUID | None = Field(
        default=None,
        description="UUID of the user who approved the document",
    )
    approved_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was approved (UTC)",
    )
    rejected_by: UUID | None = Field(
        default=None,
        description="UUID of the user who rejected the document",
    )
    rejected_reason: str | None = Field(
        default=None,
        description="Reason the document was rejected (1–2000 characters)",
    )
    rejected_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was rejected (UTC)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "document_group_id": "550e8400-e29b-41d4-a716-446655440000",
                "version": 1,
                "document_type": "policy",
                "status": "approved",
                "submitted_by": "660e8400-e29b-41d4-a716-446655440001",
                "submitted_at": "2026-07-01T10:00:00Z",
                "approved_by": "770e8400-e29b-41d4-a716-446655440002",
                "approved_at": "2026-07-02T14:30:00Z",
                "rejected_by": None,
                "rejected_reason": None,
                "rejected_at": None,
            }
        }
    }


class ApprovalQueueItem(BaseModel):
    """Lightweight item in the pending-approval queue."""

    document_id: UUID = Field(
        description="Unique document identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    document_group_id: UUID = Field(
        description="Group identifier linking all versions of the same logical document",
    )
    version: int = Field(
        description="Document version number",
        examples=[2],
    )
    document_type: DocumentType = Field(
        description="Document category",
    )
    status: Status = Field(
        description="Current lifecycle status (typically 'pending_review')",
    )
    created_by: UUID | None = Field(
        default=None,
        description="UUID of the document creator",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was created (UTC)",
    )
    submitted_by: UUID | None = Field(
        default=None,
        description="UUID of the user who submitted the document for review",
    )
    submitted_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was submitted (UTC)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "document_group_id": "550e8400-e29b-41d4-a716-446655440000",
                "version": 1,
                "document_type": "policy",
                "status": "pending_review",
                "created_by": "660e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-07-01T10:00:00Z",
                "submitted_by": "660e8400-e29b-41d4-a716-446655440001",
                "submitted_at": "2026-07-02T09:00:00Z",
            }
        }
    }


# --- Document Management schemas ---


class DocumentUploadResponse(BaseModel):
    """Result of a document upload or new-version creation."""

    document_id: UUID = Field(
        description="Unique document identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    document_group_id: UUID = Field(
        description="Group identifier linking all versions of the same logical document",
    )
    version: int = Field(
        description="Monotonically increasing version number (1-based)",
        examples=[1],
    )
    title: str = Field(
        description="Document title (derived from filename if not explicitly provided)",
        examples=["Q4 Security Policy v2"],
    )
    original_filename: str = Field(
        description="Original filename as uploaded by the user",
        examples=["q4-security-policy-v2.pdf"],
    )
    document_type: DocumentType = Field(
        description="Document category",
    )
    status: Status = Field(
        description="Current lifecycle status (typically 'draft' for new uploads)",
    )
    file_size: int | None = Field(
        default=None,
        description="File size in bytes",
        examples=[245760],
    )
    content_type: str | None = Field(
        default=None,
        description="MIME type of the uploaded file (e.g. 'application/pdf')",
        examples=["application/pdf"],
    )
    created_by: UUID | None = Field(
        default=None,
        description="UUID of the user who uploaded the document",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was created (UTC)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "document_group_id": "550e8400-e29b-41d4-a716-446655440000",
                "version": 1,
                "title": "Q4 Security Policy",
                "original_filename": "q4-security-policy.pdf",
                "document_type": "policy",
                "status": "draft",
                "file_size": 245760,
                "content_type": "application/pdf",
                "created_by": "660e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-07-01T10:00:00Z",
            }
        }
    }


class DocumentDetailResponse(BaseModel):
    """Full document details including workflow history and download URL."""

    document_id: UUID = Field(
        description="Unique document identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    document_group_id: UUID = Field(
        description="Group identifier linking all versions of the same logical document",
    )
    version: int = Field(
        description="Monotonically increasing version number (1-based)",
        examples=[3],
    )
    title: str = Field(
        description="Human-readable document title",
        examples=["Q4 Security Policy v3"],
    )
    description: str | None = Field(
        default=None,
        description="Optional description or summary of the document",
        examples=["Updated SOC 2 compliance sections for 2026."],
    )
    original_filename: str = Field(
        description="Original filename as uploaded",
        examples=["q4-security-policy.pdf"],
    )
    document_type: DocumentType = Field(
        description="Document category",
    )
    status: Status = Field(
        description="Current lifecycle status",
    )
    file_size: int | None = Field(
        default=None,
        description="File size in bytes",
        examples=[245760],
    )
    content_type: str | None = Field(
        default=None,
        description="MIME type of the stored file",
        examples=["application/pdf"],
    )
    download_url: str = Field(
        description="Presigned URL for downloading the document file (time-limited)",
        examples=["https://storage.example.com/documents/abc123.pdf?signature=..."],
    )
    rag_ingestion_status: str = Field(
        description="RAG Engine ingestion status (not_ingested, pending, ingesting, completed, failed)"
    )
    rag_ingestion_error: str | None = Field(
        default=None,
        description="Error message if RAG ingestion failed"
    )
    rag_ingested_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was last ingested into RAG (UTC)"
    )
    created_by: UUID | None = Field(
        default=None,
        description="UUID of the user who created the document",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was created (UTC)",
    )
    modified_by: UUID | None = Field(
        default=None,
        description="UUID of the user who last modified the metadata",
    )
    modified_date: datetime | None = Field(
        default=None,
        description="Timestamp of the last metadata modification (UTC)",
    )
    submitted_by: UUID | None = Field(
        default=None,
        description="UUID of the user who submitted the document for review",
    )
    submitted_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was submitted (UTC)",
    )
    approved_by: UUID | None = Field(
        default=None,
        description="UUID of the user who approved the document",
    )
    approved_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was approved (UTC)",
    )
    rejected_by: UUID | None = Field(
        default=None,
        description="UUID of the user who rejected the document",
    )
    rejected_reason: str | None = Field(
        default=None,
        description="Reason the document was rejected",
    )
    rejected_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was rejected (UTC)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "document_group_id": "550e8400-e29b-41d4-a716-446655440000",
                "version": 3,
                "title": "Q4 Security Policy v3",
                "description": "Updated SOC 2 compliance sections for 2026.",
                "original_filename": "q4-security-policy.pdf",
                "document_type": "policy",
                "status": "approved",
                "file_size": 245760,
                "content_type": "application/pdf",
                "download_url": "https://storage.example.com/documents/abc123.pdf",
                "rag_ingestion_status": "completed",
                "rag_ingestion_error": None,
                "rag_ingested_at": "2026-07-02T14:30:00Z",
                "created_by": "660e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-07-01T10:00:00Z",
                "modified_by": "660e8400-e29b-41d4-a716-446655440001",
                "modified_date": "2026-07-02T08:30:00Z",
                "submitted_by": "660e8400-e29b-41d4-a716-446655440001",
                "submitted_at": "2026-07-02T09:00:00Z",
                "approved_by": "770e8400-e29b-41d4-a716-446655440002",
                "approved_at": "2026-07-02T14:30:00Z",
                "rejected_by": None,
                "rejected_reason": None,
                "rejected_at": None,
            }
        }
    }


class DocumentListItem(BaseModel):
    """Lightweight document summary for list views."""

    document_id: UUID = Field(
        description="Unique document identifier",
    )
    document_group_id: UUID = Field(
        description="Group identifier linking all versions of the same logical document",
    )
    version: int = Field(
        description="Document version number",
    )
    title: str = Field(
        description="Human-readable document title",
    )
    original_filename: str = Field(
        description="Original filename as uploaded",
    )
    document_type: DocumentType = Field(
        description="Document category",
    )
    status: Status = Field(
        description="Current lifecycle status",
    )
    file_size: int | None = Field(
        default=None,
        description="File size in bytes",
    )
    content_type: str | None = Field(
        default=None,
        description="MIME type of the stored file",
    )
    created_by: UUID | None = Field(
        default=None,
        description="UUID of the document creator",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp when the document was created (UTC)",
    )


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""

    items: list[DocumentListItem] = Field(
        description="Document summaries for the current page",
    )
    total: int = Field(
        description="Total number of documents matching the query (across all pages)",
        examples=[150],
    )
    page: int = Field(
        description="Current page number (1-based)",
        examples=[1],
    )
    page_size: int = Field(
        description="Number of items per page (max 100)",
        examples=[20],
    )


class DocumentUpdateRequest(BaseModel):
    """Fields that can be updated on an existing document."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="New title for the document (1–500 characters, optional)",
        examples=["Q4 Security Policy — Final Approved"],
    )
    description: str | None = Field(
        default=None,
        description="Updated description or summary (optional)",
        examples=["Final approved version with all committee feedback incorporated."],
    )
    document_type: DocumentType | None = Field(
        default=None,
        description="Updated document category (optional)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Q4 Security Policy — Final Approved",
                "description": "Final approved version with all committee feedback incorporated.",
                "document_type": "policy",
            }
        }
    }


class DocumentDeleteResponse(BaseModel):
    """Confirmation of a document deletion."""

    detail: str = Field(
        description="Human-readable confirmation message",
        examples=["Document archived successfully"],
    )
    document_id: UUID = Field(
        description="UUID of the affected document",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Document archived successfully",
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    }
