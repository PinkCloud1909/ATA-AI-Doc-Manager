"""Request and response schemas for the RAG ingestion API."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


# ── Ingestion result ────────────────────────────────────────────────────────


class IngestionResponse(BaseModel):
    """Response returned after a synchronous RAG ingestion operation."""

    document_id: UUID = Field(description="Document UUID")
    status: str = Field(
        description="RAG ingestion status (completed, failed, etc.)"
    )
    rag_file_id: str | None = Field(
        default=None, description="Server-assigned RAG file ID"
    )
    processing_time_ms: float = Field(
        default=0.0,
        description="Wall-clock duration of the ingestion in milliseconds",
    )
    message: str = Field(description="Human-readable result summary")


class IngestionStatusResponse(BaseModel):
    """Current ingestion status of a document."""

    document_id: UUID
    status: str
    error_message: str | None = None
    rag_ingested_at: datetime | None = None
    title: str | None = None
    content_type: str | None = None


# ── Task accepted (async Cloud Tasks mode) ──────────────────────────────────


class TaskAcceptedResponse(BaseModel):
    """Returned when the operation was enqueued on Cloud Tasks."""

    document_id: UUID
    message: str
    task_name: str | None = None


class BulkTaskAcceptedResponse(BaseModel):
    """Returned for bulk enqueue requests."""

    accepted: list[str] = Field(default_factory=list)
    failed: list[str] = Field(default_factory=list)
    message: str = ""


# ── Bulk ingestion ──────────────────────────────────────────────────────────


class BulkIngestionRequest(BaseModel):
    """Request to ingest multiple documents at once."""

    document_ids: Annotated[
        list[UUID],
        Field(
            min_length=1,
            max_length=50,
            description="Document UUIDs to ingest (1–50)",
        ),
    ]


class BulkIngestionResponse(BaseModel):
    """Aggregated result for a bulk ingestion request."""

    results: list[IngestionResponse] = Field(default_factory=list)
    total_processed: int = 0
    total_failed: int = 0
