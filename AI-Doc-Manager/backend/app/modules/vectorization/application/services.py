import logging
import time
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import NotFoundError, ValidationError
from app.modules.documents.domain.models import Document
from app.modules.vectorization.domain.text_chunker import TextChunker
from app.modules.vectorization.domain.text_extractor import TextExtractor
from app.shared.interfaces import ILLMProvider, IObjectStorage, IVectorStore
from app.shared.utils import utcnow

logger = logging.getLogger(__name__)


@dataclass
class VectorizationResult:
    document_id: UUID
    is_vectorized: bool
    chunk_count: int
    processing_time_ms: float
    message: str


def vectorize_document(
    session: Session,
    document_id: UUID,
    storage: IObjectStorage,
    llm_provider: ILLMProvider,
    vector_store: IVectorStore,
    settings: Settings | None = None,
    force: bool = False,
) -> VectorizationResult:
    """Run the full vectorization pipeline for a single document.

    Steps:
      1. Load document from DB and validate status.
      2. Download file bytes from object storage.
      3. Extract plain text from binary content.
      4. Split text into overlapping chunks.
      5. Generate embeddings in batches via LLM provider.
      6. Upsert chunks + embeddings into vector store.
      7. Mark document as vectorized in PostgreSQL.

    Args:
        force: If True, re-vectorize even if the document is already vectorized
               (useful after a file update/replacement).
    """
    settings = settings or get_settings()
    start = time.perf_counter()
    extractor = TextExtractor()

    # 1. Load document
    document = _get_document(session, document_id)

    if document.is_vectorized and not force:
        return VectorizationResult(
            document_id=document_id,
            is_vectorized=True,
            chunk_count=0,
            processing_time_ms=0,
            message="Document is already vectorized (use force=True to re-vectorize)",
        )

    # 1b. If force re-vectorize, purge stale chunks from the previous version.
    #     Without this, a document with fewer chunks than before would leave
    #     orphaned chunks in the vector store that can be returned by semantic search.
    if force and document.is_vectorized:
        try:
            vector_store.delete_document(str(document_id))
            logger.info(
                "vectorization_stale_chunks_purged",
                extra={"document_id": str(document_id)},
            )
        except Exception as exc:
            # Non-fatal: log and continue — old chunks may linger but won't block indexing
            logger.warning(
                "vectorization_purge_failed",
                extra={"document_id": str(document_id), "error": str(exc)},
            )

    # 2. Download file from storage
    try:
        file_bytes = storage.download_object(document.file_link)
    except Exception as exc:
        logger.error(
            "vectorization_download_failed",
            extra={"document_id": str(document_id), "error": str(exc)},
        )
        raise ValidationError(f"Failed to download file: {exc}") from exc

    # 3. Extract text
    try:
        raw_text = extractor.extract(
            file_bytes,
            content_type=document.content_type,
            filename=document.original_filename,
        )
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc

    if not raw_text.strip():
        raise ValidationError("No text content could be extracted from the document")

    # 4. Chunk text
    chunker = TextChunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = chunker.chunk(raw_text)

    if not chunks:
        raise ValidationError("Text extraction produced no usable chunks")

    # 5. Generate embeddings in batches
    batch_size = settings.embedding_batch_size
    all_embeddings: list[list[float]] = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        batch_embeddings = llm_provider.generate_embeddings(
            batch, task_type="RETRIEVAL_DOCUMENT"
        )
        all_embeddings.extend(batch_embeddings)

    # 5b. Validate embedding integrity before committing to the vector store.
    #     Catches count mismatches (provider timeout / quota) and dimension errors
    #     early, with a clear error message instead of a cryptic Chroma exception.
    _validate_embeddings(chunks, all_embeddings)

    # 6. Upsert into vector store
    metadata = {
        "document_id": str(document_id),
        "title": document.title,
        "document_type": document.document_type.value,
        "original_filename": document.original_filename,
        "content_type": document.content_type or "",
        "chunk_count": len(chunks),
        "embedding_model": "gemini-embedding-2",
        "embedding_task_type": "RETRIEVAL_DOCUMENT",
        "vectorized_at": utcnow().isoformat(),
    }
    try:
        vector_store.upsert_document(
            document_id=str(document_id),
            text_chunks=chunks,
            embeddings=all_embeddings,
            metadata=metadata,
        )
    except Exception as exc:
        logger.error(
            "vectorization_upsert_failed",
            extra={"document_id": str(document_id), "error": str(exc)},
        )
        raise ValidationError(f"Failed to store vectors: {exc}") from exc

    # 7. Mark as vectorized
    try:
        document.is_vectorized = True
        document.modified_date = utcnow()
        session.commit()
    except Exception as exc:
        # Best-effort rollback of the vector store entry to avoid desync
        logger.error(
            "vectorization_db_commit_failed",
            extra={"document_id": str(document_id), "error": str(exc)},
        )
        session.rollback()
        try:
            vector_store.delete_document(str(document_id))
        except Exception as rollback_exc:
            logger.error(
                "vectorization_vector_rollback_failed",
                extra={"document_id": str(document_id), "error": str(rollback_exc)},
            )
        raise ValidationError(f"Failed to persist vectorization state: {exc}") from exc

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "document_vectorized",
        extra={
            "document_id": str(document_id),
            "chunk_count": len(chunks),
            "processing_time_ms": elapsed_ms,
        },
    )

    return VectorizationResult(
        document_id=document_id,
        is_vectorized=True,
        chunk_count=len(chunks),
        processing_time_ms=elapsed_ms,
        message="Document vectorized successfully",
    )


def delete_document_vectors(
    session: Session,
    document_id: UUID,
    vector_store: IVectorStore,
) -> None:
    """Remove all vectors for a document and reset the is_vectorized flag.

    Both steps are wrapped individually so partial failures surface clearly
    rather than silently leaving the system in an inconsistent state.
    """
    document = _get_document(session, document_id)

    # Step 1: delete from vector store
    try:
        vector_store.delete_document(str(document_id))
    except Exception as exc:
        logger.error(
            "vector_delete_failed",
            extra={"document_id": str(document_id), "error": str(exc)},
        )
        raise ValidationError(f"Failed to delete vectors: {exc}") from exc

    # Step 2: update DB flag — if this fails, vectors are already gone
    try:
        document.is_vectorized = False
        document.modified_date = utcnow()
        session.commit()
    except Exception as exc:
        logger.error(
            "vector_delete_db_commit_failed",
            extra={
                "document_id": str(document_id),
                "error": str(exc),
                "note": "Vectors deleted but DB flag not updated — manual sync required",
            },
        )
        session.rollback()
        raise ValidationError(
            "Vectors deleted but DB flag could not be updated. "
            "Manual remediation required to restore consistency."
        ) from exc

    logger.info(
        "document_vectors_deleted",
        extra={"document_id": str(document_id)},
    )


def get_vectorization_status(
    session: Session,
    document_id: UUID,
) -> dict:
    """Return the vectorization status of a document."""
    document = _get_document(session, document_id)
    return {
        "document_id": document.id,
        "is_vectorized": bool(document.is_vectorized),
        "title": document.title,
        "content_type": document.content_type,
    }


# --- helpers ---


def _get_document(session: Session, document_id: UUID) -> Document:
    document = session.execute(
        select(Document).where(Document.id == document_id)
    ).scalar_one_or_none()
    if document is None:
        raise NotFoundError("Document not found")
    return document


def _validate_embeddings(
    chunks: list[str], embeddings: list[list[float]]
) -> None:
    """Validate that embeddings align with chunks before upserting.

    Raises ``ValidationError`` if:
    - The number of embeddings doesn't match the number of chunks.
    - Any embedding is empty (zero dimensions).
    - Embeddings have inconsistent dimensions across chunks.
    """
    if len(embeddings) != len(chunks):
        raise ValidationError(
            f"Embedding count mismatch: expected {len(chunks)} "
            f"(one per chunk), got {len(embeddings)}. "
            "This may indicate a provider timeout or quota error."
        )
    if not embeddings:
        return  # already guarded by chunk count check above

    dim = len(embeddings[0])
    if dim == 0:
        raise ValidationError(
            "Embeddings have zero dimensions — the embedding model returned empty vectors."
        )
    for i, emb in enumerate(embeddings):
        if len(emb) != dim:
            raise ValidationError(
                f"Inconsistent embedding dimensions at chunk {i}: "
                f"expected {dim}, got {len(emb)}."
            )
