"""Port interfaces (ABCs) for the hexagonal adapter layer."""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Any


# ── Retrieval result types ──────────────────────────────────────────────────


@dataclass(frozen=True)
class RetrievedChunk:
    """One chunk returned by a RAG Engine retrieval."""

    text: str
    source_uri: str
    rag_file_id: str | None = None
    score: float | None = None
    distance: float | None = None
    document_id: uuid.UUID | None = None
    document_title: str | None = None


@dataclass(frozen=True)
class RagIngestResult:
    """Result of a single RAG Engine file ingestion."""

    rag_file_id: str
    rag_file_resource: str
    imported_count: int
    skipped_count: int
    failed_count: int


# ── Storage port ────────────────────────────────────────────────────────────


class IObjectStorage(ABC):
    """Port for interacting with object storage systems (Cloud Storage)."""

    @abstractmethod
    def ensure_bucket(self) -> None:
        pass

    @abstractmethod
    def upload_file(
        self, file_path: str, object_key: str, content_type: str | None = None
    ) -> str:
        pass

    @abstractmethod
    def upload_fileobj(
        self,
        file_obj: Any,
        object_key: str,
        content_type: str | None = None,
        length: int = -1,
    ) -> str:
        pass

    @abstractmethod
    def get_object_info(self, object_reference: str) -> Any:
        pass

    @abstractmethod
    def generate_presigned_download_url(
        self, object_reference: str, expires: timedelta | None = None
    ) -> str:
        pass

    @abstractmethod
    def delete_object(self, object_reference: str) -> None:
        pass

    @abstractmethod
    def build_object_key(self, filename: str, prefix: str = "documents") -> str:
        pass


# ── RAG Engine port ─────────────────────────────────────────────────────────


class IRagEngine(ABC):
    """Port for Vertex AI RAG Engine operations.

    The RAG Engine handles ingestion, chunking, embedding, and retrieval
    server-side.  This port exposes only the three operations the application
    needs: ingest a single GCS file, run a text retrieval, and delete a file.
    """

    @abstractmethod
    def ingest_file(
        self,
        document_id: str,
        gcs_uri: str,
        display_name: str | None = None,
    ) -> RagIngestResult:
        """Import one file from Cloud Storage into the RAG corpus.

        The file is chunked and embedded server-side according to the corpus
        configuration.  Returns the assigned RAG file ID and import counts.
        Raises :class:`app.core.exceptions.ExternalServiceError` on failure
        (including partial failures reported by the API).
        """
        pass

    @abstractmethod
    def retrieve(
        self,
        query_text: str,
        top_k: int = 5,
        rag_file_ids: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        """Semantic search against the RAG corpus.

        If *rag_file_ids* is provided, the search is scoped to those files.
        Raises :class:`app.core.exceptions.ExternalServiceError` on SDK error.
        """
        pass

    @abstractmethod
    def delete_file(self, rag_file_resource: str) -> None:
        """Remove a RAG file from the corpus by its full resource name.

        Idempotent — a ``NotFound`` response from the API is treated as
        success.  Other errors raise :class:`ExternalServiceError`.
        """
        pass
