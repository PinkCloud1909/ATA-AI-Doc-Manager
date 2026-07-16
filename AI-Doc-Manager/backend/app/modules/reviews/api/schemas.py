from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    """Payload to submit a document review with a grade and comment."""

    grade: int = Field(
        ge=1,
        le=10,
        description="Numeric grade from 1 (worst) to 10 (best)",
        examples=[8],
    )
    comment: str = Field(
        min_length=1,
        max_length=2000,
        description="Written feedback explaining the grade (1–2000 characters)",
        examples=["Well-written policy with clear ownership. Minor formatting nits in §3.2."],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "grade": 8,
                "comment": "Well-written policy with clear ownership. Minor formatting nits.",
            }
        }
    }


class ReviewResponse(BaseModel):
    """A document review as returned by the API."""

    id: UUID = Field(
        description="Unique review identifier",
        examples=["880e8400-e29b-41d4-a716-446655440003"],
    )
    document_id: UUID = Field(
        description="UUID of the reviewed document",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    user_id: UUID = Field(
        description="UUID of the reviewer",
        examples=["770e8400-e29b-41d4-a716-446655440002"],
    )
    grade: int = Field(
        description="Numeric grade from 1 (worst) to 10 (best)",
        examples=[8],
    )
    comment: str = Field(
        description="Written review feedback",
    )
    created_date: datetime | None = Field(
        default=None,
        description="Timestamp when the review was submitted (UTC)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440003",
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "770e8400-e29b-41d4-a716-446655440002",
                "grade": 8,
                "comment": "Well-written policy. Minor formatting nits.",
                "created_date": "2026-07-02T15:00:00Z",
            }
        }
    }


class ReviewListResponse(BaseModel):
    """Paginated list of reviews for a document."""

    items: list[ReviewResponse] = Field(
        description="Review records for the current page",
    )
    total: int = Field(
        description="Total number of reviews for the document (across all pages)",
        examples=[5],
    )
    page: int = Field(
        description="Current page number (1-based)",
        examples=[1],
    )
    page_size: int = Field(
        description="Number of items per page (1–100)",
        examples=[20],
    )
