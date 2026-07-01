"""Vertex AI Vector Search adapter.

Implements the IVectorStore interface using Vertex AI Matching Engine (Vector
Search).  This adapter is active when ENVIRONMENT=production.

Text retrieval pattern
----------------------
Vertex AI Vector Search stores only numeric vectors and string datapoint IDs.
Text is stored separately in the ``document_chunks`` PostgreSQL table (managed
by ``_persist_chunks`` in the vectorization service).

Datapoint ID format: ``{document_id}_{chunk_index}``

After ``find_neighbors`` returns IDs, this adapter resolves each ID to its text
by querying ``document_chunks``.

Restricts / metadata filtering
-------------------------------
``filter_document_ids`` translates to a Vertex AI token restriction on the
``document_id`` namespace.  Each datapoint must have been upserted with this
restriction (see ``upsert_document``).  If no filter is given, the search is
unrestricted.
"""

import logging
from typing import Any
from uuid import UUID

from google.cloud import aiplatform
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.db import get_db_session
from app.modules.documents.domain.chunk_model import DocumentChunk
from app.shared.interfaces import IVectorStore

logger = logging.getLogger(__name__)


class VertexVectorAdapter(IVectorStore):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        aiplatform.init(
            project=self.settings.gcp_project_id,
            location=self.settings.gcp_location,
        )
        self.index_endpoint_id = self.settings.vertex_index_endpoint_id
        self.deployed_index_id = self.settings.vertex_deployed_index_id
        self.index_id = self.settings.vertex_index_id

        self.index_endpoint: aiplatform.MatchingEngineIndexEndpoint | None = None
        self.index: aiplatform.MatchingEngineIndex | None = None

        if self.index_endpoint_id:
            self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
                self.index_endpoint_id
            )
        if self.index_id:
            self.index = aiplatform.MatchingEngineIndex(self.index_id)

    # ------------------------------------------------------------------
    # upsert_document
    # ------------------------------------------------------------------

    def upsert_document(
        self,
        document_id: str,
        text_chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict | None = None,
    ) -> None:
        """Push embedding vectors to the Vertex AI streaming index.

        Each datapoint carries a ``document_id`` token restriction so that
        ``semantic_search`` can filter results by document when required.

        Text is NOT pushed here — it is stored in ``document_chunks`` by the
        vectorization service before this method is called.
        """
        if not text_chunks or not self.index:
            return

        IndexDatapoint = (
            aiplatform.matching_engine.matching_engine_index_config.IndexDatapoint
        )

        datapoints = []
        for i, (_, embedding) in enumerate(zip(text_chunks, embeddings)):
            datapoint_id = f"{document_id}_{i}"
            datapoints.append(
                IndexDatapoint(
                    datapoint_id=datapoint_id,
                    feature_vector=embedding,
                    # Token restriction enables per-document filtering in
                    # semantic_search without a separate pre-filter step.
                    restricts=[
                        IndexDatapoint.Restriction(
                            namespace="document_id",
                            allow_tokens=[document_id],
                        )
                    ],
                )
            )

        self.index.upsert_datapoints(datapoints=datapoints)
        logger.debug(
            "vertex_upsert_complete",
            extra={"document_id": document_id, "datapoint_count": len(datapoints)},
        )

    # ------------------------------------------------------------------
    # semantic_search
    # ------------------------------------------------------------------

    def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_document_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Find nearest neighbors then resolve text from document_chunks.

        Returns a list of dicts with keys: id, score, text, metadata.
        Returns an empty list when the index endpoint is not configured.
        """
        if not self.index_endpoint or not self.deployed_index_id:
            logger.warning("vertex_search_skipped: index endpoint not configured")
            return []

        # Build optional token restrictions for document-level filtering.
        numeric_filter = None
        if filter_document_ids:
            numeric_filter = [
                {
                    "namespace": "document_id",
                    "allow_tokens": filter_document_ids,
                }
            ]

        try:
            response = self.index_endpoint.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=[query_embedding],
                num_neighbors=top_k,
                **({"filter": numeric_filter} if numeric_filter else {}),
            )
        except Exception as exc:
            logger.error(
                "vertex_find_neighbors_failed", extra={"error": str(exc)}
            )
            return []

        if not response or not response[0]:
            return []

        neighbors = response[0]

        # Resolve datapoint IDs to text chunks via the document_chunks table.
        results: list[dict[str, Any]] = []
        db_gen = get_db_session()
        session: Session = next(db_gen)
        try:
            results = _resolve_neighbors(session, neighbors)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        return results

    # ------------------------------------------------------------------
    # delete_document
    # ------------------------------------------------------------------

    def delete_document(self, document_id: str) -> None:
        """Remove all vectors for *document_id* from the Vertex index.

        Queries ``document_chunks`` to discover all chunk indices (and therefore
        all datapoint IDs), then calls ``remove_datapoints``.

        The corresponding ``document_chunks`` rows are deleted by the
        vectorization service (``delete_document_vectors``) which calls this
        method first.  We only need to remove the vectors here.
        """
        if not self.index:
            logger.warning("vertex_delete_skipped: index not configured")
            return

        # Fetch chunk indices from the DB to build datapoint IDs.
        db_gen = get_db_session()
        session: Session = next(db_gen)
        try:
            doc_uuid = UUID(document_id)
            chunk_indices: list[int] = list(
                session.execute(
                    select(DocumentChunk.chunk_index).where(
                        DocumentChunk.document_id == doc_uuid
                    )
                ).scalars()
            )
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

        if not chunk_indices:
            logger.debug(
                "vertex_delete_noop",
                extra={"document_id": document_id, "reason": "no chunks found"},
            )
            return

        datapoint_ids = [f"{document_id}_{i}" for i in chunk_indices]
        try:
            self.index.remove_datapoints(datapoint_ids=datapoint_ids)
        except Exception as exc:
            logger.error(
                "vertex_remove_datapoints_failed",
                extra={"document_id": document_id, "error": str(exc)},
            )
            raise

        logger.debug(
            "vertex_delete_complete",
            extra={
                "document_id": document_id,
                "removed_count": len(datapoint_ids),
            },
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _resolve_neighbors(
    session: Session,
    neighbors: list[Any],
) -> list[dict[str, Any]]:
    """Fetch text + metadata for each neighbor from ``document_chunks``.

    Neighbors whose IDs cannot be resolved (e.g. stale index entries for
    deleted documents) are silently skipped.

    Args:
        session:   Active SQLAlchemy Session.
        neighbors: Neighbour list from ``index_endpoint.find_neighbors()``.

    Returns:
        List of result dicts in the same format as ChromaVectorAdapter.
    """
    if not neighbors:
        return []

    # Parse datapoint IDs: format is "{document_id}_{chunk_index}"
    # The document_id itself may contain underscores (it's a UUID with hyphens)
    # so we split on the LAST underscore only.
    parsed: list[tuple[str, UUID, int, float]] = []  # (dp_id, doc_uuid, chunk_idx, score)
    for neighbor in neighbors:
        dp_id: str = neighbor.id
        distance: float = neighbor.distance
        last_sep = dp_id.rfind("_")
        if last_sep == -1:
            logger.warning("vertex_bad_datapoint_id", extra={"id": dp_id})
            continue
        doc_id_str = dp_id[:last_sep]
        chunk_idx_str = dp_id[last_sep + 1:]
        try:
            doc_uuid = UUID(doc_id_str)
            chunk_idx = int(chunk_idx_str)
        except (ValueError, AttributeError):
            logger.warning("vertex_bad_datapoint_id", extra={"id": dp_id})
            continue
        parsed.append((dp_id, doc_uuid, chunk_idx, distance))

    if not parsed:
        return []

    # Batch-fetch all matching rows in one query.
    # Build (document_id, chunk_index) tuples for the IN-style filter.
    from sqlalchemy import and_, or_, tuple_ as sa_tuple

    conditions = or_(
        *[
            and_(
                DocumentChunk.document_id == doc_uuid,
                DocumentChunk.chunk_index == chunk_idx,
            )
            for _, doc_uuid, chunk_idx, _ in parsed
        ]
    )
    rows: list[DocumentChunk] = list(
        session.execute(select(DocumentChunk).where(conditions)).scalars()
    )

    # Index fetched rows by (document_id, chunk_index) for O(1) lookup.
    row_index: dict[tuple[UUID, int], DocumentChunk] = {
        (r.document_id, r.chunk_index): r for r in rows
    }

    results: list[dict[str, Any]] = []
    for dp_id, doc_uuid, chunk_idx, distance in parsed:
        chunk = row_index.get((doc_uuid, chunk_idx))
        if chunk is None:
            # Stale vector in the index — no matching text row.
            logger.warning(
                "vertex_stale_datapoint",
                extra={"datapoint_id": dp_id},
            )
            continue
        results.append(
            {
                "id": dp_id,
                "score": distance,
                "text": chunk.text,
                "metadata": {
                    "document_id": str(doc_uuid),
                    "chunk_index": chunk_idx,
                    "embedding_model": chunk.embedding_model,
                },
            }
        )

    return results
