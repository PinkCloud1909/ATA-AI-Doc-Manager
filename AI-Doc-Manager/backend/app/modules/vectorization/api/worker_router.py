"""Internal Cloud Tasks worker endpoint for asynchronous vectorization.

This router exposes a single route:

    POST /api/v1/vectorization/worker/{document_id}

It is called exclusively by Cloud Tasks via an OIDC-authenticated HTTP request.
Public internet traffic must NOT be able to reach this route.

Security model
--------------
Cloud Run + Cloud Tasks: the OIDC token in the Authorization header is
validated by Cloud Run automatically when the service requires authentication.
No additional token-parsing logic is needed here — if the request reaches this
handler, Cloud Run has already validated the OIDC token.

However, an extra header check (X-CloudTasks-QueueName) is performed as a
defence-in-depth measure to confirm the request came from Cloud Tasks and not
from an accidentally authenticated caller.

In local development: the queue header check is skipped because is_async_mode()
is False and this endpoint is never reached via the normal router (it is only
registered in main.py unconditionally for completeness).
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.db import get_db_session
from app.modules.vectorization.application.services import vectorize_document
from app.shared.adapters.factory import get_llm_provider, get_object_storage, get_vector_store
from app.shared.interfaces import ILLMProvider, IObjectStorage, IVectorStore
from app.shared.task_publisher import is_async_mode

logger = logging.getLogger(__name__)

worker_router = APIRouter(
    prefix="/api/v1/vectorization/worker",
    tags=["vectorization-worker"],
    include_in_schema=False,  # Hidden from public OpenAPI docs
)


def _get_storage() -> IObjectStorage:
    return get_object_storage()


def _get_vectors() -> IVectorStore:
    return get_vector_store()


def _get_llm() -> ILLMProvider:
    return get_llm_provider()


@worker_router.post("/{document_id}", status_code=204)
def worker_vectorize(
    document_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    storage: Annotated[IObjectStorage, Depends(_get_storage)],
    llm: Annotated[ILLMProvider, Depends(_get_llm)],
    vectors: Annotated[IVectorStore, Depends(_get_vectors)],
    force: bool = Query(default=False),
    # Cloud Tasks injects this header on every request.
    # Its presence confirms the caller is Cloud Tasks (defence-in-depth).
    x_cloudtasks_queuename: str | None = Header(default=None),
) -> None:
    """Execute vectorization for a single document (called by Cloud Tasks).

    Returns 204 No Content on success.
    Returns 400 if the request did not come from Cloud Tasks (missing queue header
    in production).
    Returns 500 on vectorization failure — Cloud Tasks will retry automatically.
    """
    settings: Settings = get_settings()

    # In production, reject requests that lack the Cloud Tasks queue header.
    # This prevents accidentally triggering expensive work from other callers.
    if is_async_mode(settings) and not x_cloudtasks_queuename:
        logger.warning(
            "worker_rejected_missing_queue_header",
            extra={"document_id": str(document_id)},
        )
        raise HTTPException(
            status_code=400,
            detail="Missing X-CloudTasks-QueueName header",
        )

    logger.info(
        "worker_vectorize_start",
        extra={
            "document_id": str(document_id),
            "force": force,
            "queue": x_cloudtasks_queuename,
        },
    )

    vectorize_document(
        session,
        document_id=document_id,
        storage=storage,
        llm_provider=llm,
        vector_store=vectors,
        force=force,
    )

    logger.info(
        "worker_vectorize_complete",
        extra={"document_id": str(document_id)},
    )
    # 204 No Content — Cloud Tasks considers any 2xx a success.
    return None
