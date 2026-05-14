import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.core.dependencies import require_permission
from app.modules.iam.domain.principal import AuthenticatedUser
from app.modules.vectorization.api.schemas import (
    BulkVectorizationRequest,
    BulkVectorizationResponse,
    VectorizationResponse,
    VectorizationStatusResponse,
)
from app.modules.vectorization.application.services import (
    delete_document_vectors,
    get_vectorization_status,
    vectorize_document,
)
from app.shared.adapters.factory import (
    get_llm_provider,
    get_object_storage,
    get_vector_store,
)
from app.shared.interfaces import ILLMProvider, IObjectStorage, IVectorStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vectorization", tags=["vectorization"])


def _get_storage() -> IObjectStorage:
    return get_object_storage()


def _get_vectors() -> IVectorStore:
    return get_vector_store()


def _get_llm() -> ILLMProvider:
    return get_llm_provider()


# NOTE: /bulk route MUST be registered BEFORE /{document_id} to avoid
# FastAPI interpreting the literal string "bulk" as a UUID path parameter.
@router.post(
    "/bulk",
    response_model=BulkVectorizationResponse,
    summary="Bulk vectorize multiple documents",
)
def bulk_vectorize_route(
    payload: BulkVectorizationRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    storage: Annotated[IObjectStorage, Depends(_get_storage)],
    llm: Annotated[ILLMProvider, Depends(_get_llm)],
    vectors: Annotated[IVectorStore, Depends(_get_vectors)],
    force: bool = Query(default=False, description="Re-vectorize even if already vectorized"),
) -> BulkVectorizationResponse:
    results: list[VectorizationResponse] = []
    failed = 0

    for doc_id in payload.document_ids:
        try:
            result = vectorize_document(
                session,
                document_id=doc_id,
                storage=storage,
                llm_provider=llm,
                vector_store=vectors,
                force=force,
            )
            results.append(
                VectorizationResponse(
                    document_id=result.document_id,
                    is_vectorized=result.is_vectorized,
                    chunk_count=result.chunk_count,
                    processing_time_ms=result.processing_time_ms,
                    message=result.message,
                )
            )
        except Exception as exc:
            failed += 1
            # Best-effort rollback so the SQLAlchemy session is in a clean state
            # before processing the next document in the batch.
            try:
                session.rollback()
            except Exception:
                pass
            results.append(
                VectorizationResponse(
                    document_id=doc_id,
                    is_vectorized=False,
                    chunk_count=0,
                    processing_time_ms=0,
                    message=f"Failed: {exc}",
                )
            )
            logger.warning(
                "bulk_vectorize_item_failed",
                extra={"document_id": str(doc_id), "error": str(exc)},
            )

    return BulkVectorizationResponse(
        results=results,
        total_processed=len(results) - failed,
        total_failed=failed,
    )


@router.post(
    "/{document_id}",
    response_model=VectorizationResponse,
    summary="Vectorize a single document",
)
def vectorize_document_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    storage: Annotated[IObjectStorage, Depends(_get_storage)],
    llm: Annotated[ILLMProvider, Depends(_get_llm)],
    vectors: Annotated[IVectorStore, Depends(_get_vectors)],
    force: bool = Query(default=False, description="Re-vectorize even if already vectorized"),
) -> VectorizationResponse:
    result = vectorize_document(
        session,
        document_id=document_id,
        storage=storage,
        llm_provider=llm,
        vector_store=vectors,
        force=force,
    )
    return VectorizationResponse(
        document_id=result.document_id,
        is_vectorized=result.is_vectorized,
        chunk_count=result.chunk_count,
        processing_time_ms=result.processing_time_ms,
        message=result.message,
    )


@router.delete(
    "/{document_id}",
    response_model=VectorizationResponse,
    summary="Delete vectors for a document",
)
def delete_vectors_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
    vectors: Annotated[IVectorStore, Depends(_get_vectors)],
) -> VectorizationResponse:
    delete_document_vectors(session, document_id=document_id, vector_store=vectors)
    return VectorizationResponse(
        document_id=document_id,
        is_vectorized=False,
        chunk_count=0,
        processing_time_ms=0,
        message="Document vectors deleted successfully",
    )


@router.get(
    "/{document_id}/status",
    response_model=VectorizationStatusResponse,
    summary="Get vectorization status of a document",
)
def vectorization_status_route(
    document_id: UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission())],
    session: Annotated[Session, Depends(get_db_session)],
) -> VectorizationStatusResponse:
    status = get_vectorization_status(session, document_id=document_id)
    return VectorizationStatusResponse(**status)
