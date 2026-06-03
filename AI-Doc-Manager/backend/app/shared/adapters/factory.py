import os
from functools import lru_cache

from app.core.config import Settings, get_settings
from app.shared.adapters.chroma_vector_adapter import ChromaVectorAdapter
from app.shared.adapters.gcs_storage_adapter import GCSStorageAdapter
from app.shared.adapters.google_ai_llm_adapter import GoogleAILlmAdapter
from app.shared.adapters.minio_storage_adapter import MinioStorageAdapter
from app.shared.adapters.vertex_ai_llm_adapter import VertexAILlmAdapter
from app.shared.adapters.vertex_vector_adapter import VertexVectorAdapter
from app.shared.interfaces import ILLMProvider, IObjectStorage, IVectorStore


@lru_cache()
def get_object_storage(settings: Settings | None = None) -> IObjectStorage:
    settings = settings or get_settings()
    env = os.getenv("ENV", "local").lower()

    if env == "prod":
        return GCSStorageAdapter(settings)
    return MinioStorageAdapter(settings)


@lru_cache()
def get_vector_store(settings: Settings | None = None) -> IVectorStore:
    settings = settings or get_settings()
    env = os.getenv("ENV", "local").lower()

    if env == "prod":
        return VertexVectorAdapter(settings)
    return ChromaVectorAdapter(settings)


@lru_cache()
def get_llm_provider(settings: Settings | None = None) -> ILLMProvider:
    settings = settings or get_settings()
    env = os.getenv("ENV", "local").lower()

    if env == "prod":
        return VertexAILlmAdapter(settings)
    return GoogleAILlmAdapter(settings)
