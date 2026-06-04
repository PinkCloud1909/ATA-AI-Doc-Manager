from typing import Any

import chromadb

from app.core.config import Settings, get_settings
from app.shared.interfaces import IVectorStore


class ChromaVectorAdapter(IVectorStore):
    """ChromaDB adapter for local/dev vector store.

    Client selection priority:
      1. HttpClient  — when ``chroma_host`` is configured (remote Chroma server).
      2. EphemeralClient — when ``chroma_ephemeral=True`` (unit tests only; data is lost on restart).
      3. PersistentClient — default; data survives restarts (recommended for local dev).

    The collection is always created with:
      - ``embedding_function=None``: embeddings are provided explicitly by the LLM adapter.
      - ``hnsw:space=cosine``: cosine distance matches the normalized output of Google's
        text-embedding-004 model and gives more intuitive similarity scores.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

        if self.settings.chroma_host:
            self.client = chromadb.HttpClient(
                host=self.settings.chroma_host,
                port=self.settings.chroma_port,
            )
        elif self.settings.chroma_ephemeral:
            # In-memory only — data lost on restart. Use ONLY in tests.
            self.client = chromadb.EphemeralClient()
        else:
            # Default: persist to disk so vectors survive process restarts.
            # Without this, PostgreSQL marks documents as vectorized but ChromaDB
            # has nothing — semantic search silently returns empty results.
            self.client = chromadb.PersistentClient(
                path=self.settings.chroma_persist_path
            )

        self.collection = self.client.get_or_create_collection(
            name=self.settings.chroma_collection,
            # We supply embeddings manually; do not let Chroma apply its own function.
            embedding_function=None,
            # Cosine distance suits normalized text embeddings (Google text-embedding-004).
            # Must be set at collection creation time and cannot be changed later.
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_document(
        self,
        document_id: str,
        text_chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict | None = None,
    ) -> None:
        if not text_chunks:
            return

        ids = [f"{document_id}_{i}" for i in range(len(text_chunks))]
        # Always include document_id and chunk_index for filtered deletes and
        # for the QA agent to display source attribution.
        base_meta = {**(metadata or {}), "document_id": document_id}
        metadatas = [{**base_meta, "chunk_index": i} for i in range(len(text_chunks))]

        self.collection.upsert(
            documents=text_chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_document_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        where_clause = None
        if filter_document_ids:
            if len(filter_document_ids) == 1:
                where_clause = {"document_id": filter_document_ids[0]}
            else:
                where_clause = {"document_id": {"$in": filter_document_ids}}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        matches: list[dict[str, Any]] = []
        if not results["documents"] or not results["documents"][0]:
            return matches

        for doc, meta, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # With cosine distance space: distance ∈ [0, 2].
            # Convert to cosine *similarity* ∈ [-1, 1] (higher = more similar).
            # For normalized vectors (Google embeddings): similarity ≈ 1 - distance.
            similarity = round(1.0 - distance, 6)
            matches.append(
                {
                    "text": doc,
                    "metadata": meta,
                    "distance": distance,   # raw distance (lower = more similar)
                    "score": similarity,    # cosine similarity (higher = more similar)
                }
            )

        return matches

    def delete_document(self, document_id: str) -> None:
        """Remove all chunks belonging to *document_id* from the collection."""
        self.collection.delete(where={"document_id": document_id})
