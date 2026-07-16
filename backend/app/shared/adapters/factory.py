from functools import lru_cache

from app.core.config import Settings, get_settings
from app.shared.adapters.gcs_storage_adapter import GCSStorageAdapter
from app.shared.adapters.rag_engine_adapter import RagEngineAdapter
from app.shared.interfaces import IObjectStorage, IRagEngine


@lru_cache()
def get_object_storage(settings: Settings | None = None) -> IObjectStorage:
    """Return the Cloud Storage adapter (GCS is used in every environment)."""
    settings = settings or get_settings()
    return GCSStorageAdapter(settings)


@lru_cache()
def get_rag_engine(settings: Settings | None = None) -> IRagEngine:
    """Return the Vertex AI RAG Engine adapter (used in every environment)."""
    settings = settings or get_settings()
    return RagEngineAdapter(settings)
