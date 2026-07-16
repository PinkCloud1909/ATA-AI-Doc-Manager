"""RAG ingestion API — public endpoints.

``/api/v1/rag/*`` endpoints for triggering, checking, and deleting
RAG Engine ingestion of approved documents.
"""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db_session, session_scope
from app.core.dependencies import require_permission
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.rag.api.schemas import (
    BulkIngestionRequest,
    BulkIngestionResponse,
    BulkTaskAcceptedResponse,
    IngestionResponse,
    IngestionStatusResponse,
    TaskAcceptedResponse,
)
from app.modules.rag.application.services import (
    delete_document_ingestion,
    get_ingestion_status,
    ingest_document,
    mark_ingestion_pending,
)
from app.shared.adapters.factory import get_rag_engine
from app.shared.interfaces import IRagEngine
from app.shared.openapi_helpers import DELETE_RESPONSES, MUTATE_RESPONSES
from app.shared.task_publisher import enqueue_rag_ingestion_task, is_async_mode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])


def _get_rag_engine_dep() -> IRagEngine:
    return get_rag_engine()


# NOTE: /bulk route MUST be registered BEFORE /{document_id} to avoid
# FastAPI interpreting the literal string "bulk" as a UUID path parameter.
@router.post(
    "/bulk",
    response_model=BulkIngestionResponse | BulkTaskAcceptedResponse,
    summary="Bulk ingest multiple documents into RAG Engine",
    status_code=202,
    description=(
        "Ingest multiple documents in a single request.\n\n"
        "- **Production** (async Cloud Tasks): "
        "Each document is enqueued as an independent Cloud Tasks task.  "
        "Returns 202 Accepted immediately.\n"
        "- **Local / dev**: Runs synchronously in-request.  "
        "Each document is processed in an isolated database transaction so a "
        "failure in one does not roll back prior successes."
    ),
    response_description="Ingestion results (sync mode) or task acceptance (async mode)",
    responses={
        202: {"description": "Tasks enqueued for asynchronous processing"},
        **MUTATE_RESPONSES,
    },
)
def bulk_ingest_route(
    payload: BulkIngestionRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    rag_engine: Annotated[IRagEngine, Depends(_get_rag_engine_dep)],
    force: bool = Query(
        default=False, description="Re-ingest even if already completed"
    ),
) -> BulkIngestionResponse | BulkTaskAcceptedResponse:
    settings = get_settings()

    if is_async_mode(settings):
        accepted: list[str] = []
        failed: list[str] = []
        for doc_id in payload.document_ids:
            try:
                enqueue_rag_ingestion_task(
                    document_id=str(doc_id),
                    force=force,
                    settings=settings,
                )
                # Mark the document as PENDING so the status is visible
                # before the Cloud Tasks worker picks it up.
                try:
                    with session_scope() as s:
                        mark_ingestion_pending(s, doc_id)
                except Exception as exc:
                    logger.warning(
                        "mark_pending_failed",
                        extra={"document_id": str(doc_id), "error": str(exc)},
                    )
                accepted.append(str(doc_id))
            except Exception as exc:
                logger.error(
                    "bulk_enqueue_failed",
                    extra={"document_id": str(doc_id), "error": str(exc)},
                )
                failed.append(str(doc_id))
        return BulkTaskAcceptedResponse(
            accepted=accepted,
            failed=failed,
            message=(
                f"Enqueued {len(accepted)} task(s); "
                f"{len(failed)} failed to enqueue."
            ),
        )

    # --- synchronous (local dev) path ---
    results: list[IngestionResponse] = []
    failed_count = 0

    for doc_id in payload.document_ids:
        try:
            with session_scope() as isolated_session:
                result = ingest_document(
                    isolated_session,
                    document_id=doc_id,
                    rag_engine=rag_engine,
                    force=force,
                )
            results.append(
                IngestionResponse(
                    document_id=result.document_id,
                    status=result.status,
                    rag_file_id=result.rag_file_id,
                    processing_time_ms=result.processing_time_ms,
                    message=result.message,
                )
            )
        except Exception as exc:
            failed_count += 1
            results.append(
                IngestionResponse(
                    document_id=doc_id,
                    status="failed",
                    processing_time_ms=0.0,
                    message=f"Failed: {exc}",
                )
            )
            logger.warning(
                "bulk_ingest_item_failed",
                extra={"document_id": str(doc_id), "error": str(exc)},
            )

    return BulkIngestionResponse(
        results=results,
        total_processed=len(results) - failed_count,
        total_failed=failed_count,
    )


@router.post(
    "/{document_id}",
    response_model=TaskAcceptedResponse | IngestionResponse,
    summary="Ingest a single document into RAG Engine",
    status_code=202,
    description=(
        "Ingest a single approved document for semantic search and RAG.\n\n"
        "- **Production** (async Cloud Tasks): "
        "Enqueues a Cloud Tasks task and returns 202 Accepted immediately.  "
        "The actual ingestion runs asynchronously via the worker endpoint.\n"
        "- **Local / dev**: Runs synchronously and returns the full result.\n\n"
        "Set ``force=true`` to re-ingest a document that has already been "
        "processed (required after changing the layout parser config)."
    ),
    response_description="Ingestion result (sync) or task acceptance (async)",
    responses={
        202: {"description": "Task enqueued for asynchronous processing"},
        404: {"description": "Document not found"},
        **MUTATE_RESPONSES,
    },
)
def ingest_document_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    rag_engine: Annotated[IRagEngine, Depends(_get_rag_engine_dep)],
    force: bool = Query(
        default=False, description="Re-ingest even if already completed"
    ),
) -> TaskAcceptedResponse | IngestionResponse:
    settings = get_settings()

    if is_async_mode(settings):
        task_name = enqueue_rag_ingestion_task(
            document_id=str(document_id),
            force=force,
            settings=settings,
        )
        # Mark PENDING so status reflects the enqueued task.
        mark_ingestion_pending(session, document_id)
        return TaskAcceptedResponse(
            document_id=document_id,
            message="RAG ingestion task enqueued",
            task_name=task_name,
        )

    # --- synchronous (local dev) path ---
    result = ingest_document(
        session,
        document_id=document_id,
        rag_engine=rag_engine,
        force=force,
    )
    return IngestionResponse(
        document_id=result.document_id,
        status=result.status,
        rag_file_id=result.rag_file_id,
        processing_time_ms=result.processing_time_ms,
        message=result.message,
    )


@router.delete(
    "/{document_id}",
    response_model=IngestionResponse,
    summary="Delete RAG ingestion data for a document",
    description=(
        "Removes the document's RAG file from the corpus and resets its "
        "ingestion status.  The document file in Cloud Storage is not affected."
    ),
    response_description="Confirmation that ingestion data was deleted",
    responses={
        404: {"description": "Document not found"},
        **DELETE_RESPONSES,
    },
)
def delete_ingestion_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    rag_engine: Annotated[IRagEngine, Depends(_get_rag_engine_dep)],
) -> IngestionResponse:
    delete_document_ingestion(session, document_id=document_id, rag_engine=rag_engine)
    return IngestionResponse(
        document_id=document_id,
        status="not_ingested",
        message="RAG ingestion data deleted successfully",
    )


@router.get(
    "/{document_id}/status",
    response_model=IngestionStatusResponse,
    summary="Get RAG ingestion status of a document",
    description=(
        "Lightweight check returning the document's current RAG ingestion "
        "status, error message (if failed), and timestamps."
    ),
    response_description="Current ingestion status",
    responses={
        404: {"description": "Document not found"},
        **MUTATE_RESPONSES,
    },
)
def ingestion_status_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> IngestionStatusResponse:
    status = get_ingestion_status(session, document_id=document_id)
    return IngestionStatusResponse(**status)
