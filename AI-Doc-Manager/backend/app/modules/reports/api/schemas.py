from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReportSummary(BaseModel):
    total: int
    draft: int
    pending_review: int
    approved: int
    rejected: int
    expired: int


class ApprovalRate(BaseModel):
    approved: int
    rejected: int
    rate: float


class AvgGradeByType(BaseModel):
    document_type: str
    avg_grade: float
    count: int


class ActivityItem(BaseModel):
    user: str
    action: str
    document_id: UUID
    timestamp: datetime
