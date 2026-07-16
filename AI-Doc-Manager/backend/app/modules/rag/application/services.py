"""RAG ingestion orchestration.

All functions accept the caller's ``Session`` so mapping writes and ingestion
status transitions happen in a single database transaction.  The
``RagEngineAdapter`` is a pure SDK wrapper — it holds no DB state.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import NotFoundError
from app.modules.documents.domain.models import Document
from app.modules.rag.domain.enums import RagIngestionStatus
from app.modules.rag.domain.rag_file_mapping_model import RagFileMapping
from app.shared.interfaces import IRagEngine
from app.shared.utils import utcnow

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """Result of a single document's RAG ingestion."""

    document_id: UUID
    status: str
    rag_file_id: str | None = None
    processing_time_ms: float = 0.0
    message: str = ""


def ingest_document(
    session: Session,
    document_id: UUID,
    rag_engine: IRagEngine,
    settings: Settings | None = None,
    force: bool = False,
) -> IngestionResult:
    """Ingest a document into the RAG Engine corpus.

    Loads the document, imports its GCS file via ``rag_engine.ingest_file``,
    persists a mapping row, and updates ingestion status to ``COMPLETED``.

    When *force* is True, any existing RAG file is first deleted from the
    corpus (required for layout-parser changes — the RAG Engine will not
    re-import a file with a new parser config otherwise).

    Raises ``NotFoundError`` when the document does not exist.
    Raises ``ExternalServiceError`` (via the adapter) on import failure.
    On failure the document status is set to ``FAILED`` and the error
    message persisted before the exception propagates.
    """
    settings = settings or get_settings()
    start = time.perf_counter()

    document = _get_document(session, document_id)

    if document.rag_ingestion_status == RagIngestionStatus.COMPLETED and not force:
        return IngestionResult(
            document_id=document_id,
            status=RagIngestionStatus.COMPLETED.value,
            message=(
                "Document is already ingested. Use force=true to re-ingest."
            ),
        )

    # -- Mark ingesting so pollers see progress ------------------------------
    document.rag_ingestion_status = RagIngestionStatus.INGESTING
    document.modified_date = utcnow()
    session.commit()

    # -- If force re-ingest, delete the existing RAG file first --------------
    # Required by the layout-parser rule: files imported without the parser
    # are NOT re-imported when the parser is enabled later.
    if force:
        existing = _get_existing_mapping(session, document_id)
        if existing is not None:
            try:
                rag_engine.delete_file(existing.rag_file_resource)
                session.delete(existing)
                session.commit()
                logger.info(
                    "rag_ingestion_purged_for_force",
                    extra={
                        "document_id": str(document_id),
                        "rag_file_resource": existing.rag_file_resource,
                    },
                )
            except Exception:
                logger.warning(
                    "rag_ingestion_purge_failed",
                    extra={"document_id": str(document_id)},
                    exc_info=True,
                )
                # Continue anyway — the new import may succeed.

    # -- Import into RAG Engine ----------------------------------------------
    try:
        result = rag_engine.ingest_file(
            document_id=str(document_id),
            gcs_uri=document.file_link,
            display_name=document.title,
        )
    except Exception as exc:
        document.rag_ingestion_status = RagIngestionStatus.FAILED
        document.rag_ingestion_error = str(exc)[:2000]
        document.modified_date = utcnow()
        session.commit()
        logger.error(
            "rag_ingestion_failed",
            extra={"document_id": str(document_id), "error": str(exc)},
        )
        raise

    # -- Persist mapping + mark completed ------------------------------------
    _upsert_mapping(
        session,
        document_id=document_id,
        rag_corpus_resource=rag_engine.corpus_name,
        rag_file_id=result.rag_file_id,
        rag_file_resource=result.rag_file_resource,
    )
    document.rag_ingestion_status = RagIngestionStatus.COMPLETED
    document.rag_ingested_at = utcnow()
    document.rag_ingestion_error = None
    document.modified_date = utcnow()
    session.commit()

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "rag_ingestion_complete",
        extra={
            "document_id": str(document_id),
            "rag_file_id": result.rag_file_id,
            "processing_time_ms": elapsed_ms,
        },
    )
    return IngestionResult(
        document_id=document_id,
        status=RagIngestionStatus.COMPLETED.value,
        rag_file_id=result.rag_file_id,
        processing_time_ms=elapsed_ms,
        message="Document ingested into RAG Engine",
    )


def mark_ingestion_pending(session: Session, document_id: UUID) -> None:
    """Set a document's RAG ingestion status to PENDING (async enqueued).

    This is called immediately after a Cloud Tasks task is successfully
    enqueued so the status reflects that work is scheduled.
    """
    document = _get_document(session, document_id)
    document.rag_ingestion_status = RagIngestionStatus.PENDING
    document.modified_date = utcnow()
    session.commit()


def delete_document_ingestion(
    session: Session,
    document_id: UUID,
    rag_engine: IRagEngine,
) -> None:
    """Remove a document from the RAG corpus and reset its status.

    Deletes the RAG file (idempotent), removes the mapping row,
    and sets status back to ``NOT_INGESTED``.
    """
    document = _get_document(session, document_id)
    mapping = _get_existing_mapping(session, document_id)

    if mapping is not None:
        rag_engine.delete_file(mapping.rag_file_resource)
        session.delete(mapping)

    document.rag_ingestion_status = RagIngestionStatus.NOT_INGESTED
    document.rag_ingested_at = None
    document.rag_ingestion_error = None
    document.modified_date = utcnow()
    session.commit()

    logger.info(
        "rag_ingestion_deleted",
        extra={"document_id": str(document_id)},
    )


def get_ingestion_status(session: Session, document_id: UUID) -> dict:
    """Return the RAG ingestion status of a document."""
    document = _get_document(session, document_id)
    return {
        "document_id": document.id,
        "status": document.rag_ingestion_status.value,
        "error_message": document.rag_ingestion_error,
        "rag_ingested_at": document.rag_ingested_at,
        "title": document.title,
        "content_type": document.content_type,
    }


# ---------------------------------------------------------------------------
# Internal helpers (same session — callers must provide it)
# ---------------------------------------------------------------------------


def _get_document(session: Session, document_id: UUID) -> Document:
    document = session.execute(
        select(Document).where(Document.id == document_id)
    ).scalar_one_or_none()
    if document is None:
        raise NotFoundError("Document not found")
    return document


def _get_existing_mapping(
    session: Session, document_id: UUID
) -> RagFileMapping | None:
    return session.execute(
        select(RagFileMapping).where(
            RagFileMapping.document_id == document_id,
        )
    ).scalar_one_or_none()


def _upsert_mapping(
    session: Session,
    document_id: UUID,
    rag_corpus_resource: str,
    rag_file_id: str,
    rag_file_resource: str,
) -> RagFileMapping:
    """Insert or update a rag_file_mappings row."""
    existing = session.execute(
        select(RagFileMapping).where(
            RagFileMapping.document_id == document_id,
            RagFileMapping.rag_corpus_resource == rag_corpus_resource,
        )
    ).scalar_one_or_none()

    now = utcnow()
    if existing is not None:
        existing.rag_file_id = rag_file_id
        existing.rag_file_resource = rag_file_resource
        existing.imported_at = now
        existing.updated_at = now
        return existing

    mapping = RagFileMapping(
        document_id=document_id,
        rag_corpus_resource=rag_corpus_resource,
        rag_file_id=rag_file_id,
        rag_file_resource=rag_file_resource,
        imported_at=now,
        created_at=now,
        updated_at=now,
    )
    session.add(mapping)
    return mapping
