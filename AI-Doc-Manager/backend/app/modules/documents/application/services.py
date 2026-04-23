import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.modules.documents.domain.models import Document
from app.shared.enums import Status
from app.shared.utils import utcnow

logger = logging.getLogger(__name__)


def get_document_by_id(session: Session, document_id: UUID) -> Document:
    document = session.execute(
        select(Document).where(Document.id == document_id)
    ).scalar_one_or_none()
    if document is None:
        logger.warning("document_not_found", extra={"document_id": str(document_id)})
        raise NotFoundError("Document not found")
    return document


def submit_document_for_review(
    session: Session,
    document_id: UUID,
    user_id: UUID,
) -> Document:
    document = get_document_by_id(session, document_id)
    if document.status not in {Status.DRAFT, Status.REJECTED}:
        raise ConflictError("Only draft or rejected documents can be submitted for review")

    now = utcnow()
    document.status = Status.PENDING_REVIEW
    document.submitted_by = user_id
    document.submitted_at = now
    document.rejected_by = None
    document.rejected_at = None
    document.rejected_reason = None
    document.modified_by = user_id
    document.modified_date = now
    session.commit()
    return document


def approve_document(
    session: Session,
    document_id: UUID,
    user_id: UUID,
) -> tuple[Document, list[Document]]:
    document = get_document_by_id(session, document_id)
    if document.status != Status.PENDING_REVIEW:
        raise ConflictError("Only pending documents can be approved")

    now = utcnow()
    expired_documents = session.execute(
        select(Document).where(
            Document.document_group_id == document.document_group_id,
            Document.status == Status.APPROVED,
            Document.id != document.id,
        )
    ).scalars().all()
    for expired in expired_documents:
        expired.status = Status.EXPIRED
        expired.modified_by = user_id
        expired.modified_date = now

    document.status = Status.APPROVED
    document.approved_by = user_id
    document.approved_at = now
    document.rejected_by = None
    document.rejected_at = None
    document.rejected_reason = None
    document.modified_by = user_id
    document.modified_date = now
    session.commit()
    return document, expired_documents


def reject_document(
    session: Session,
    document_id: UUID,
    user_id: UUID,
    reason: str,
) -> Document:
    document = get_document_by_id(session, document_id)
    if document.status != Status.PENDING_REVIEW:
        raise ConflictError("Only pending documents can be rejected")
    if not reason.strip():
        raise ValidationError("Rejection reason is required")

    now = utcnow()
    document.status = Status.REJECTED
    document.rejected_by = user_id
    document.rejected_at = now
    document.rejected_reason = reason
    document.modified_by = user_id
    document.modified_date = now
    session.commit()
    return document


def list_pending_approvals(session: Session) -> list[Document]:
    return (
        session.execute(
            select(Document).where(Document.status == Status.PENDING_REVIEW)
        )
        .scalars()
        .all()
    )
