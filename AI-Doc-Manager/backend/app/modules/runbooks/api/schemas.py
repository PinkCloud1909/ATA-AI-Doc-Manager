from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class RunbookPurpose(str, Enum):
    ONBOARDING = "onboarding"
    INCIDENT_RESPONSE = "incident_response"
    DEPLOYMENT = "deployment"
    TROUBLESHOOTING = "troubleshooting"
    TRAINING = "training"
    OTHER = "other"


class RunbookGenerateRequest(BaseModel):
    document_ids: list[UUID] = Field(..., min_length=1, max_length=10)
    purpose: RunbookPurpose
    title: str | None = Field(default=None, min_length=1, max_length=500)


class RunbookResponse(BaseModel):
    runbook_id: UUID
    title: str
    purpose: RunbookPurpose
    document_ids: list[UUID]
    content: str | None = None
    status: str
    error_message: str | None = None
    created_by: UUID | None = None
    created_at: datetime | None = None
    modified_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RunbookListItem(BaseModel):
    runbook_id: UUID
    title: str
    purpose: RunbookPurpose
    document_ids: list[UUID]
    status: str
    created_by: UUID | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RunbookListResponse(BaseModel):
    items: list[RunbookListItem]
    total: int
    page: int
    page_size: int
