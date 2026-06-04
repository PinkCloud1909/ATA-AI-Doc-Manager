import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any


class IObjectStorage(ABC):
    """Port for interacting with object storage systems (e.g. MinIO, GCS)."""

    @abstractmethod
    def ensure_bucket(self) -> None:
        pass

    @abstractmethod
    def upload_file(self, file_path: str, object_key: str, content_type: str | None = None) -> str:
        pass

    @abstractmethod
    def upload_fileobj(self, file_obj: Any, object_key: str, content_type: str | None = None, length: int = -1) -> str:
        pass

    @abstractmethod
    def get_object_info(self, object_reference: str) -> Any:
        pass

    @abstractmethod
    def generate_presigned_download_url(self, object_reference: str, expires: timedelta | None = None) -> str:
        pass

    @abstractmethod
    def delete_object(self, object_reference: str) -> None:
        pass

    @abstractmethod
    def download_object(self, object_reference: str) -> bytes:
        """Download the entire file content as bytes."""
        pass

    @abstractmethod
    def build_object_key(self, filename: str, prefix: str = "documents") -> str:
        pass


class IVectorStore(ABC):
    """Port for vector database operations (e.g. ChromaDB, Vertex AI Vector Search)."""

    @abstractmethod
    def upsert_document(self, document_id: str, text_chunks: list[str], embeddings: list[list[float]], metadata: dict | None = None) -> None:
        pass

    @abstractmethod
    def semantic_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_document_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        pass


class ILLMProvider(ABC):
    """Port for LLM and Embedding models (e.g. Google AI Gemini, Vertex AI)."""

    @abstractmethod
    def generate_embeddings(
        self,
        texts: list[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed.
            task_type: Embedding task type for optimization.
                - ``RETRIEVAL_DOCUMENT`` — indexing corpus/document chunks (default).
                - ``RETRIEVAL_QUERY``    — general semantic search query.
                - ``QUESTION_ANSWERING`` — natural-language questions for QA.
                - ``FACT_VERIFICATION`` — fact-checking statements.
        """
        pass

    @abstractmethod
    def generate_response(self, prompt: str, context: list[str]) -> str:
        pass
