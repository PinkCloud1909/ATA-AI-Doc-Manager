"""Internal Cloud Tasks worker endpoint for async RAG ingestion.

This router exposes a single route:

    POST /api/v1/rag/worker/{document_id}

It is called exclusively by Cloud Tasks via an OIDC-authenticated HTTP request.
The handler performs the actual ``ingest_document`` call that was previously
enqueued by the public ``POST /api/v1/rag/{document_id}`` endpoint.

Security model
--------------
Two layers of defence (applied explicitly because the Cloud Run service is
publicly invokable):

1. **OIDC ID token** (primary) — ``verify_worker_token()`` validates the
   Google-signed JWT that Cloud Tasks attaches.
2. **X-CloudTasks-QueueName** (defence-in-depth) — confirms the request
   arrived through Cloud Tasks.

In local development both checks are skipped (``is_async_mode`` returns False).
"""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.db import get_db_session
from app.modules.rag.api.worker_auth import verify_worker_token
from app.modules.rag.application.services import ingest_document
from app.shared.adapters.factory import get_rag_engine
from app.shared.interfaces import IRagEngine
from app.shared.task_publisher import is_async_mode

logger = logging.getLogger(__name__)

worker_router = APIRouter(
    prefix="/api/v1/rag/worker",
    tags=["rag-worker"],
    include_in_schema=False,  # Hidden from public OpenAPI docs
)


def _get_rag_engine_dep() -> IRagEngine:
    return get_rag_engine()


@worker_router.post("/{document_id}", status_code=204)
def worker_ingest(
    document_id: UUID,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    rag_engine: Annotated[IRagEngine, Depends(_get_rag_engine_dep)],
    force: bool = Query(default=False),
    x_cloudtasks_queuename: str | None = Header(default=None),
    x_cloudtasks_taskretrycount: str | None = Header(default=None),
    x_cloudtasks_taskname: str | None = Header(default=None),
) -> None:
    """Execute RAG ingestion for a single document (called by Cloud Tasks).

    **Idempotent**: ``ingest_document`` checks the ingestion status — a
    ``COMPLETED`` document is skipped when *force* is False.

    Returns 204 No Content on success (Cloud Tasks treats any 2xx as success).
    Returns 401 if the OIDC token is missing or invalid.
    Returns 400 if the ``X-CloudTasks-QueueName`` header is absent.
    Returns 500 on ingestion failure — Cloud Tasks will retry automatically.
    """
    settings: Settings = get_settings()

    # Primary auth: verify the OIDC ID token Cloud Tasks attaches.
    verify_worker_token(request, settings)

    # Defence-in-depth: reject requests lacking the queue header.
    if is_async_mode(settings) and not x_cloudtasks_queuename:
        logger.warning(
            "worker_rejected_missing_queue_header",
            extra={"document_id": str(document_id)},
        )
        raise HTTPException(
            status_code=400,
            detail="Missing X-CloudTasks-QueueName header",
        )

    retry_count = (
        int(x_cloudtasks_taskretrycount) if x_cloudtasks_taskretrycount else 0
    )

    logger.info(
        "worker_ingest_start",
        extra={
            "document_id": str(document_id),
            "force": force,
            "queue": x_cloudtasks_queuename,
            "task_name": x_cloudtasks_taskname,
            "retry_count": retry_count,
        },
    )

    result = ingest_document(
        session,
        document_id=document_id,
        rag_engine=rag_engine,
        force=force,
    )

    logger.info(
        "worker_ingest_complete",
        extra={
            "document_id": str(document_id),
            "task_name": x_cloudtasks_taskname,
            "status": result.status,
            "rag_file_id": result.rag_file_id,
            "processing_time_ms": result.processing_time_ms,
            "retry_count": retry_count,
        },
    )
    return None
