"""RAG retrieval with document-title enrichment.

The RAG Engine adapter returns raw ``RetrievedChunk`` objects with only the
chunk text, source URI, and score.  This service enriches them with the
originating document's ID and title by reverse-mapping the RAG file IDs
returned in the chunk metadata.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import session_scope
from app.modules.documents.domain.models import Document
from app.modules.rag.domain.rag_file_mapping_model import RagFileMapping
from app.shared.adapters.factory import get_rag_engine
from app.shared.interfaces import RetrievedChunk

logger = logging.getLogger(__name__)


def retrieve_chunks(
    query: str,
    top_k: int = 5,
    document_ids: list[UUID] | None = None,
) -> list[RetrievedChunk]:
    """Semantic search with optional document-scope filtering and title enrichment.

    When *document_ids* is provided, only chunks belonging to those documents
    are considered.  If no matching RAG file mappings exist for the given
    document IDs an empty list is returned (the search is NOT widened to the
    whole corpus).  Results are enriched with ``document_id`` and
    ``document_title`` from the PostgreSQL documents table.
    """
    rag_engine = get_rag_engine()

    # -- Resolve filter document_ids → rag_file_ids --------------------------
    rag_file_ids: list[str] | None = None
    if document_ids:
        with session_scope() as session:
            rag_file_ids = _resolve_rag_file_ids(session, document_ids)

        if not rag_file_ids:
            # No matching RAG files for the requested docs → nothing to search.
            return []

    # -- Execute retrieval ---------------------------------------------------
    chunks = rag_engine.retrieve(
        query_text=query,
        top_k=top_k,
        rag_file_ids=rag_file_ids,
    )

    if not chunks:
        return []

    # -- Enrich with document metadata ---------------------------------------
    _enrich_chunks(chunks)

    return chunks


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_rag_file_ids(
    session: Session, document_ids: list[UUID]
) -> list[str]:
    """Return RAG file IDs for the given documents (only mapped ones)."""
    rows = list(
        session.execute(
            select(RagFileMapping.rag_file_id).where(
                RagFileMapping.document_id.in_(document_ids),
            )
        ).scalars()
    )
    return rows


def _enrich_chunks(chunks: list[RetrievedChunk]) -> None:
    """Batch-map ``rag_file_id`` → document title and attach to chunks."""
    # Collect unique RAG file IDs from chunks.
    rag_file_ids: set[str] = {c.rag_file_id for c in chunks if c.rag_file_id}
    if not rag_file_ids:
        return

    with session_scope() as session:
        rows = list(
            session.execute(
                select(
                    RagFileMapping.rag_file_id,
                    Document.id,
                    Document.title,
                )
                .join(Document, RagFileMapping.document_id == Document.id)
                .where(RagFileMapping.rag_file_id.in_(rag_file_ids))
            )
        )

    # Build lookup: rag_file_id → (document_id, document_title)
    lookup: dict[str, tuple[UUID, str]] = {}
    for row in rows:
        lookup[row[0]] = (row[1], row[2])

    for chunk in chunks:
        if chunk.rag_file_id and chunk.rag_file_id in lookup:
            doc_id, doc_title = lookup[chunk.rag_file_id]
            # The chunk is frozen; use object.__setattr__ to enrich.
            object.__setattr__(chunk, "document_id", doc_id)
            object.__setattr__(chunk, "document_title", doc_title)
