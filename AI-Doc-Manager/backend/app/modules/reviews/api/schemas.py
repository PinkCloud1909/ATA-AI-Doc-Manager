from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    grade: int = Field(ge=1, le=10)
    comment: str = Field(min_length=1, max_length=2000)


class ReviewResponse(BaseModel):
    id: UUID
    document_id: UUID
    user_id: UUID
    grade: int
    comment: str
    created_date: datetime | None = None
