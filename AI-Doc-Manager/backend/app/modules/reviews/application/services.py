from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ValidationError
from app.modules.documents.application.services import get_document_by_id
from app.modules.reviews.domain.models import DocumentReview
from app.shared.enums import Status
from app.shared.utils import utcnow


def create_review(
    session: Session,
    document_id: UUID,
    user_id: UUID,
    grade: int,
    comment: str,
) -> DocumentReview:
    if grade < 1 or grade > 10:
        raise ValidationError("Grade must be between 1 and 10")
    if not comment.strip():
        raise ValidationError("Comment is required")

    document = get_document_by_id(session, document_id)
    if document.status not in {Status.PENDING_REVIEW, Status.APPROVED}:
        raise ConflictError("Reviews are only allowed for pending or approved documents")

    review = DocumentReview(
        document_id=document.id,
        user_id=user_id,
        grade=grade,
        comment=comment,
        created_date=utcnow(),
    )
    session.add(review)
    session.commit()
    return review


def list_reviews(
    session: Session,
    document_id: UUID,
    *,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[DocumentReview], int]:
    """Return a paginated list of reviews for a document, newest first."""
    get_document_by_id(session, document_id)

    total = (
        session.execute(
            select(func.count())
            .select_from(DocumentReview)
            .where(DocumentReview.document_id == document_id)
        ).scalar()
        or 0
    )

    offset = (page - 1) * page_size
    reviews = (
        session.execute(
            select(DocumentReview)
            .where(DocumentReview.document_id == document_id)
            .order_by(DocumentReview.created_date.desc())
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )

    return list(reviews), total

