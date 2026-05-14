from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "dms-backend"
    environment: str = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/dms_backend"
    )
    async_database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/dms_backend"
    )
    google_api_key: str | None = None

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    minio_endpoint: str = "localhost:9000"
    minio_external_endpoint: str | None = None
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket: str = "documents"
    minio_presigned_expiry_minutes: int = 15
    max_upload_size_mb: int = 50

    default_admin_username: str = Field(default="admin", max_length=100)
    default_admin_password: str = Field(default="admin123", min_length=8)
    default_admin_role_name: str = Field(default="admin", max_length=50)
    default_user_role_name: str = Field(default="user", max_length=50)

    # Vectorization settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_batch_size: int = 20

    # ChromaDB settings
    # Default port 8001 avoids conflict with FastAPI which runs on 8000
    chroma_host: str | None = None
    chroma_port: int = 8001
    chroma_collection: str = "document_chunks"
    # Path for PersistentClient (used when chroma_host is None and chroma_ephemeral is False).
    # Relative paths are resolved from the working directory (project root).
    chroma_persist_path: str = "./.chroma_data"
    # Set to True ONLY in tests/dev where data loss on restart is acceptable.
    chroma_ephemeral: bool = False

    # GCP / Vertex AI settings (required when ENV=prod)
    gcp_project_id: str | None = None
    gcp_location: str = "us-central1"
    vertex_index_id: str | None = None
    vertex_index_endpoint_id: str | None = None
    vertex_deployed_index_id: str | None = None

    @property
    def google_ai_api_key(self) -> str | None:
        """Alias for google_api_key for backward compatibility."""
        return self.google_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
