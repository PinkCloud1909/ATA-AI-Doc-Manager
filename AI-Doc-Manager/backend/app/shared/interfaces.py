import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class IObjectStorage(ABC):
    """Port for interacting with object storage systems (e.g. MinIO, GCS)."""

    @abstractmethod
    def ensure_bucket(self) -> None:
        pass

    @abstractmethod
    def upload_file(self, file_path: str, object_key: str, content_type: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def upload_fileobj(self, file_obj: Any, object_key: str, content_type: Optional[str] = None, length: int = -1) -> str:
        pass

    @abstractmethod
    def get_object_info(self, object_reference: str) -> Any:
        pass

    @abstractmethod
    def generate_presigned_download_url(self, object_reference: str, expires: Optional[timedelta] = None) -> str:
        pass

    @abstractmethod
    def delete_object(self, object_reference: str) -> None:
        pass

    @abstractmethod
    def build_object_key(self, filename: str, prefix: str = "documents") -> str:
        pass


class IVectorStore(ABC):
    """Port for vector database operations (e.g. ChromaDB, Vertex AI Vector Search)."""

    @abstractmethod
    def upsert_document(self, document_id: str, text_chunks: List[str], embeddings: List[List[float]], metadata: Optional[Dict] = None) -> None:
        pass

    @abstractmethod
    def semantic_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        pass


class ILLMProvider(ABC):
    """Port for LLM and Embedding models (e.g. Google AI Gemini, Vertex AI)."""

    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def generate_response(self, prompt: str, context: List[str]) -> str:
        pass
