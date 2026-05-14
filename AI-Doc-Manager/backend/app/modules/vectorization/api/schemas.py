from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class VectorizationResponse(BaseModel):
    document_id: UUID
    is_vectorized: bool
    chunk_count: int
    processing_time_ms: float
    message: str


class VectorizationStatusResponse(BaseModel):
    document_id: UUID
    is_vectorized: bool
    title: str
    content_type: str | None = None


class BulkVectorizationRequest(BaseModel):
    document_ids: list[UUID] = Field(..., min_length=1, max_length=50)


class BulkVectorizationResponse(BaseModel):
    results: list[VectorizationResponse]
    total_processed: int
    total_failed: int
