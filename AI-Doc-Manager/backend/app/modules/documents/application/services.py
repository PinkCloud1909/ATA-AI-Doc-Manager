import logging
import uuid
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.modules.documents.domain.models import Document
from app.modules.reviews.domain.models import DocumentReview
from app.shared.enums import DocumentType, Status
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


def _next_version(session: Session, document_group_id: UUID) -> int:
    current = session.execute(
        select(func.max(Document.version)).where(
            Document.document_group_id == document_group_id
        )
    ).scalar_one_or_none()
    return int(current or 0) + 1


def create_document(
    session: Session,
    document_type: DocumentType,
    file_link: str,
    user_id: UUID,
    *,
    title: str | None = None,
    description: str | None = None,
    original_filename: str | None = None,
    file_size: int | None = None,
    content_type: str | None = None,
    document_group_id: UUID | None = None,
) -> Document:
    now = utcnow()
    group_id = document_group_id or uuid.uuid4()
    version = _next_version(session, group_id) if document_group_id else 1
    document = Document(
        document_group_id=group_id,
        version=version,
        document_type=document_type,
        status=Status.DRAFT,
        title=(title or original_filename or "Untitled").strip(),
        description=description,
        original_filename=original_filename or title or "unknown",
        file_link=file_link,
        file_size=file_size,
        content_type=content_type,
        is_vectorized=False,
        created_by=user_id,
        created_at=now,
        modified_by=user_id,
        modified_date=now,
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


def create_new_version(
    session: Session,
    document_id: UUID,
    file_link: str,
    user_id: UUID,
    *,
    title: str | None = None,
    description: str | None = None,
    original_filename: str | None = None,
    file_size: int | None = None,
    content_type: str | None = None,
) -> Document:
    original = get_document_by_id(session, document_id)
    now = utcnow()
    new_version = Document(
        document_group_id=original.document_group_id,
        version=_next_version(session, original.document_group_id),
        document_type=original.document_type,
        status=Status.DRAFT,
        title=(title or original.title).strip(),
        description=description if description is not None else original.description,
        original_filename=original_filename or original.original_filename,
        file_link=file_link,
        file_size=file_size,
        content_type=content_type or original.content_type,
        is_vectorized=False,
        created_by=user_id,
        created_at=now,
        modified_by=user_id,
        modified_date=now,
    )
    session.add(new_version)
    session.commit()
    session.refresh(new_version)
    return new_version


def update_document_metadata(
    session: Session,
    document_id: UUID,
    user_id: UUID,
    *,
    title: str | None = None,
    description: str | None = None,
    document_type: DocumentType | None = None,
) -> Document:
    document = get_document_by_id(session, document_id)
    if document.status != Status.DRAFT:
        raise ConflictError("Only draft documents can be edited")
    if title is not None:
        document.title = title.strip()
    if description is not None:
        document.description = description
    if document_type is not None:
        document.document_type = document_type
    document.modified_by = user_id
    document.modified_date = utcnow()
    session.commit()
    session.refresh(document)
    return document


def list_documents(
    session: Session,
    *,
    status_filter: Status | None = None,
    document_type: DocumentType | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Document], int]:
    stmt = select(Document)
    count_stmt = select(func.count()).select_from(Document)
    filters = []
    if status_filter is not None:
        filters.append(Document.status == status_filter)
    if document_type is not None:
        filters.append(Document.document_type == document_type)
    if search:
        filters.append(Document.title.ilike(f"%{search}%"))
    if filters:
        stmt = stmt.where(*filters)
        count_stmt = count_stmt.where(*filters)

    total = session.execute(count_stmt).scalar_one()
    safe_page = max(page, 1)
    safe_size = min(max(page_size, 1), 100)
    documents = (
        session.execute(
            stmt.order_by(Document.created_at.desc(), Document.version.desc())
            .offset((safe_page - 1) * safe_size)
            .limit(safe_size)
        )
        .scalars()
        .all()
    )
    return documents, total


def get_document_versions(session: Session, document_group_id: UUID) -> list[Document]:
    return (
        session.execute(
            select(Document)
            .where(Document.document_group_id == document_group_id)
            .order_by(Document.version.desc())
        )
        .scalars()
        .all()
    )


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
    session.refresh(document)
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
    session.refresh(document)
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
    session.refresh(document)
    return document


def archive_document(session: Session, document_id: UUID, user_id: UUID) -> Document:
    document = get_document_by_id(session, document_id)
    if document.status == Status.ARCHIVED:
        raise ConflictError("Document is already archived")
    document.status = Status.ARCHIVED
    document.modified_by = user_id
    document.modified_date = utcnow()
    session.commit()
    session.refresh(document)
    return document


def permanently_delete_document(session: Session, document_id: UUID) -> Document:
    document = get_document_by_id(session, document_id)
    session.delete(document)
    session.commit()
    return document


def list_pending_approvals(session: Session) -> list[Document]:
    return (
        session.execute(
            select(Document)
            .where(Document.status == Status.PENDING_REVIEW)
            .order_by(Document.submitted_at.desc())
        )
        .scalars()
        .all()
    )


def average_grade(session: Session, document_id: UUID) -> float | None:
    value = session.execute(
        select(func.avg(DocumentReview.grade)).where(
            DocumentReview.document_id == document_id
        )
    ).scalar_one_or_none()
    return float(value) if value is not None else None
