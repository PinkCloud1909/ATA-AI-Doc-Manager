import logging
import uuid
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.modules.documents.domain.models import Document
from app.shared.interfaces import IObjectStorage, IRagEngine
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


def create_document(
    session: Session,
    *,
    title: str,
    original_filename: str,
    file_link: str,
    document_type: DocumentType,
    user_id: UUID,
    file_size: int | None = None,
    content_type: str | None = None,
    description: str | None = None,
) -> Document:
    now = utcnow()
    document = Document(
        document_group_id=uuid.uuid4(),
        version=1,
        document_type=document_type,
        status=Status.DRAFT,
        title=title,
        description=description,
        original_filename=original_filename,
        file_link=file_link,
        file_size=file_size,
        content_type=content_type,
        created_by=user_id,
        created_at=now,
        modified_by=user_id,
        modified_date=now,
    )
    session.add(document)
    session.commit()
    logger.info(
        "document_created",
        extra={
            "document_id": str(document.id),
            "document_group_id": str(document.document_group_id),
        },
    )
    return document


def list_documents(
    session: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    status_filter: Status | None = None,
    document_type_filter: DocumentType | None = None,
    created_by_filter: UUID | None = None,
    allowed_statuses: set[Status] | None = None,
) -> tuple[list[Document], int]:
    query = select(Document)
    count_query = select(func.count()).select_from(Document)

    # Role-based status filtering: restrict to allowed statuses
    if allowed_statuses is not None:
        query = query.where(Document.status.in_(allowed_statuses))
        count_query = count_query.where(Document.status.in_(allowed_statuses))

    if status_filter is not None:
        # If user-supplied filter conflicts with allowed statuses, return empty
        if allowed_statuses and status_filter not in allowed_statuses:
            return [], 0
        query = query.where(Document.status == status_filter)
        count_query = count_query.where(Document.status == status_filter)
    if document_type_filter is not None:
        query = query.where(Document.document_type == document_type_filter)
        count_query = count_query.where(Document.document_type == document_type_filter)
    if created_by_filter is not None:
        query = query.where(Document.created_by == created_by_filter)
        count_query = count_query.where(Document.created_by == created_by_filter)

    total = session.execute(count_query).scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(Document.created_at.desc()).offset(offset).limit(page_size)
    documents = session.execute(query).scalars().all()

    return documents, total


def get_document_detail(
    session: Session,
    document_id: UUID,
    storage: IObjectStorage,
) -> tuple[Document, str]:
    document = get_document_by_id(session, document_id)
    download_url = storage.generate_presigned_download_url(document.file_link)
    return document, download_url


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
        raise ConflictError("Only draft documents can be updated")

    now = utcnow()
    if title is not None:
        document.title = title
    if description is not None:
        document.description = description
    if document_type is not None:
        document.document_type = document_type
    document.modified_by = user_id
    document.modified_date = now
    session.commit()
    logger.info("document_updated", extra={"document_id": str(document_id)})
    return document


def archive_document(
    session: Session,
    document_id: UUID,
    user_id: UUID,
) -> Document:
    document = get_document_by_id(session, document_id)
    if document.status == Status.ARCHIVED:
        raise ConflictError("Document is already archived")

    now = utcnow()
    document.status = Status.ARCHIVED
    document.modified_by = user_id
    document.modified_date = now
    session.commit()
    logger.info("document_archived", extra={"document_id": str(document_id)})
    return document


def delete_document_permanently(
    session: Session,
    document_id: UUID,
    storage: IObjectStorage,
    rag_engine: IRagEngine,
) -> None:
    document = get_document_by_id(session, document_id)
    file_link = document.file_link

    # Remove the RAG file from the corpus first (best-effort) — the mapping
    # row must be read before the document row is deleted (FK CASCADE would
    # remove it).  A failure here must not block the document deletion.
    try:
        from app.modules.rag.domain.rag_file_mapping_model import (  # noqa: PLC0415
            RagFileMapping,
        )

        mapping = session.execute(
            select(RagFileMapping).where(RagFileMapping.document_id == document_id)
        ).scalar_one_or_none()
        if mapping is not None:
            rag_engine.delete_file(mapping.rag_file_resource)
            session.delete(mapping)
    except Exception as exc:
        logger.warning(
            "rag_delete_failed",
            extra={"document_id": str(document_id), "error": str(exc)},
        )

    session.delete(document)
    session.commit()

    try:
        storage.delete_object(file_link)
    except Exception:
        logger.warning(
            "storage_delete_failed",
            extra={"document_id": str(document_id), "file_link": file_link},
        )

    logger.info("document_deleted_permanently", extra={"document_id": str(document_id)})


def create_new_version(
    session: Session,
    *,
    source_document_id: UUID,
    file_link: str,
    original_filename: str,
    user_id: UUID,
    file_size: int | None = None,
    content_type: str | None = None,
    title: str | None = None,
    description: str | None = None,
) -> Document:
    source = get_document_by_id(session, source_document_id)

    max_version = (
        session.execute(
            select(func.max(Document.version)).where(
                Document.document_group_id == source.document_group_id
            )
        ).scalar()
        or 0
    )

    now = utcnow()
    new_doc = Document(
        document_group_id=source.document_group_id,
        version=max_version + 1,
        document_type=source.document_type,
        status=Status.DRAFT,
        title=title or source.title,
        description=description if description is not None else source.description,
        original_filename=original_filename,
        file_link=file_link,
        file_size=file_size,
        content_type=content_type,
        created_by=user_id,
        created_at=now,
        modified_by=user_id,
        modified_date=now,
    )
    session.add(new_doc)
    session.commit()
    logger.info(
        "document_new_version",
        extra={
            "document_id": str(new_doc.id),
            "document_group_id": str(new_doc.document_group_id),
            "version": new_doc.version,
        },
    )
    return new_doc


def submit_document_for_review(
    session: Session,
    document_id: UUID,
    user_id: UUID,
) -> Document:
    document = get_document_by_id(session, document_id)
    if document.status not in {Status.DRAFT, Status.REJECTED}:
        raise ConflictError(
            "Only draft or rejected documents can be submitted for review"
        )

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
    expired_documents = (
        session.execute(
            select(Document).where(
                Document.document_group_id == document.document_group_id,
                Document.status == Status.APPROVED,
                Document.id != document.id,
            )
        )
        .scalars()
        .all()
    )
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

    # Vectorization is triggered by the caller (router) as a background task
    # to avoid blocking the HTTP response. See documents/api/router.py.
    logger.info("document_approved", extra={"document_id": str(document_id)})
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


def expire_document(
    session: Session,
    document_id: UUID,
    user_id: UUID,
) -> Document:
    """Mark an approved document as expired."""
    document = get_document_by_id(session, document_id)
    if document.status != Status.APPROVED:
        raise ConflictError("Only approved documents can be marked as expired")

    now = utcnow()
    document.status = Status.EXPIRED
    document.modified_by = user_id
    document.modified_date = now
    session.commit()
    logger.info("document_expired", extra={"document_id": str(document_id)})
    return document


def average_grade(session: Session, document_id: UUID) -> float | None:
    value = session.execute(
        select(func.avg(DocumentReview.grade)).where(
            DocumentReview.document_id == document_id
        )
    ).scalar_one_or_none()
    return float(value) if value is not None else None
