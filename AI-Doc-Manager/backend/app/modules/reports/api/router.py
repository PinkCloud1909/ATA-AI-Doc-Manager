from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.documents.domain.models import Document
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.reports.api.schemas import (
    ActivityItem,
    ApprovalRate,
    AvgGradeByType,
    ReportSummary,
)
from app.modules.reviews.domain.models import DocumentReview
from app.shared.enums import Status

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/summary", response_model=ReportSummary, status_code=status.HTTP_200_OK)
def get_summary(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> ReportSummary:
    rows = session.execute(
        select(Document.status, func.count(Document.id)).group_by(Document.status)
    ).all()
    counts = {status_value: count for status_value, count in rows}

    return ReportSummary(
        total=sum(counts.values()),
        draft=counts.get(Status.DRAFT, 0),
        pending_review=counts.get(Status.PENDING_REVIEW, 0),
        approved=counts.get(Status.APPROVED, 0),
        rejected=counts.get(Status.REJECTED, 0),
        expired=counts.get(Status.EXPIRED, 0),
    )


@router.get(
    "/approval-rate",
    response_model=ApprovalRate,
    status_code=status.HTTP_200_OK,
)
def get_approval_rate(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> ApprovalRate:
    rows = session.execute(
        select(Document.status, func.count(Document.id))
        .where(Document.status.in_([Status.APPROVED, Status.REJECTED]))
        .group_by(Document.status)
    ).all()
    counts = {status_value: count for status_value, count in rows}
    approved = counts.get(Status.APPROVED, 0)
    rejected = counts.get(Status.REJECTED, 0)
    decided = approved + rejected

    return ApprovalRate(
        approved=approved,
        rejected=rejected,
        rate=(approved / decided) if decided else 0,
    )


@router.get(
    "/avg-grade",
    response_model=list[AvgGradeByType],
    status_code=status.HTTP_200_OK,
)
def get_avg_grade(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> list[AvgGradeByType]:
    rows = session.execute(
        select(
            Document.document_type,
            func.avg(DocumentReview.grade),
            func.count(DocumentReview.id),
        )
        .join(DocumentReview, DocumentReview.document_id == Document.id)
        .group_by(Document.document_type)
        .order_by(Document.document_type)
    ).all()

    return [
        AvgGradeByType(
            document_type=document_type.value,
            avg_grade=float(avg_grade or 0),
            count=count,
        )
        for document_type, avg_grade, count in rows
    ]


@router.get(
    "/activity",
    response_model=list[ActivityItem],
    status_code=status.HTTP_200_OK,
)
def get_activity(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    limit: int = Query(20, ge=1, le=100),
) -> list[ActivityItem]:
    activity_time = func.coalesce(
        Document.rejected_at,
        Document.approved_at,
        Document.submitted_at,
        Document.modified_date,
        Document.created_at,
    )
    documents = session.execute(
        select(Document)
        .where(activity_time.is_not(None))
        .order_by(desc(activity_time))
        .limit(limit)
    ).scalars().all()

    items: list[ActivityItem] = []
    for document in documents:
        if document.rejected_at:
            action = "rejected"
            timestamp = document.rejected_at
        elif document.approved_at:
            action = "approved"
            timestamp = document.approved_at
        elif document.submitted_at:
            action = "submitted"
            timestamp = document.submitted_at
        elif document.modified_date:
            action = "updated"
            timestamp = document.modified_date
        else:
            action = "created"
            timestamp = document.created_at

        if timestamp is None:
            continue

        items.append(
            ActivityItem(
                user=document.creator.username if document.creator else "system",
                action=action,
                document_id=document.id,
                timestamp=timestamp,
            )
        )

    return items
