from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RunbookPurpose(str, Enum):
    """Intended use case for the runbook — drives generation style and structure."""

    ONBOARDING = "onboarding"
    INCIDENT_RESPONSE = "incident_response"
    DEPLOYMENT = "deployment"
    TROUBLESHOOTING = "troubleshooting"
    TRAINING = "training"
    OTHER = "other"


class RunbookGenerateRequest(BaseModel):
    """Payload to trigger runbook generation from a set of documents."""

    document_ids: list[UUID] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of document UUIDs to synthesize into a runbook (1–10 documents)",
        examples=[["550e8400-e29b-41d4-a716-446655440000", "660e8400-e29b-41d4-a716-446655440001"]],
    )
    purpose: RunbookPurpose = Field(
        description="Intended use case — drives the structure and tone of the generated runbook",
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Optional custom title for the runbook (auto-generated if omitted)",
        examples=["SOC 2 Compliance Incident Response Runbook"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "660e8400-e29b-41d4-a716-446655440001",
                ],
                "purpose": "incident_response",
                "title": "SOC 2 Compliance Incident Response Runbook",
            }
        }
    )


class RunbookResponse(BaseModel):
    """A generated runbook with full content and metadata."""

    runbook_id: UUID = Field(
        description="Unique runbook identifier",
        examples=["990e8400-e29b-41d4-a716-446655440004"],
    )
    title: str = Field(
        description="Runbook title",
        examples=["SOC 2 Compliance Incident Response Runbook"],
    )
    purpose: RunbookPurpose = Field(
        description="Purpose category used for generation",
    )
    document_ids: list[UUID] = Field(
        description="UUIDs of the documents used as source material",
    )
    content: str | None = Field(
        default=None,
        description="Generated markdown content (null if generation failed or is still in progress)",
    )
    status: str = Field(
        description="Generation status: 'pending', 'generating', 'completed', or 'failed'",
        examples=["completed"],
    )
    error_message: str | None = Field(
        default=None,
        description="Error details if generation failed",
    )
    created_by: UUID | None = Field(
        default=None,
        description="UUID of the user who requested generation",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp when the runbook was created (UTC)",
    )
    modified_date: datetime | None = Field(
        default=None,
        description="Timestamp of the last modification (UTC)",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "runbook_id": "990e8400-e29b-41d4-a716-446655440004",
                "title": "SOC 2 Compliance Incident Response Runbook",
                "purpose": "incident_response",
                "document_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "660e8400-e29b-41d4-a716-446655440001",
                ],
                "content": "# Incident Response Runbook\n\n## Overview\n...",
                "status": "completed",
                "error_message": None,
                "created_by": "660e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-07-03T10:00:00Z",
                "modified_date": "2026-07-03T10:00:00Z",
            }
        },
    )


class RunbookListItem(BaseModel):
    """Lightweight runbook summary for list views (no generated content)."""

    runbook_id: UUID = Field(
        description="Unique runbook identifier",
    )
    title: str = Field(
        description="Runbook title",
    )
    purpose: RunbookPurpose = Field(
        description="Purpose category",
    )
    document_ids: list[UUID] = Field(
        description="UUIDs of the source documents",
    )
    status: str = Field(
        description="Generation status",
    )
    created_by: UUID | None = Field(
        default=None,
        description="UUID of the requesting user",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Timestamp when the runbook was created (UTC)",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "runbook_id": "990e8400-e29b-41d4-a716-446655440004",
                "title": "SOC 2 Compliance Incident Response Runbook",
                "purpose": "incident_response",
                "document_ids": [
                    "550e8400-e29b-41d4-a716-446655440000",
                    "660e8400-e29b-41d4-a716-446655440001",
                ],
                "status": "completed",
                "created_by": "660e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-07-03T10:00:00Z",
            }
        },
    )


class RunbookDeleteResponse(BaseModel):
    """Confirmation of a runbook deletion."""

    detail: str = Field(
        description="Human-readable confirmation message",
        examples=["Runbook deleted successfully"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {"detail": "Runbook deleted successfully"}
        }
    }


class RunbookListResponse(BaseModel):
    """Paginated list of runbooks."""

    items: list[RunbookListItem] = Field(
        description="Runbook summaries for the current page",
    )
    total: int = Field(
        description="Total number of runbooks matching the query (across all pages)",
        examples=[12],
    )
    page: int = Field(
        description="Current page number (1-based)",
        examples=[1],
    )
    page_size: int = Field(
        description="Number of items per page (max 100)",
        examples=[20],
    )
