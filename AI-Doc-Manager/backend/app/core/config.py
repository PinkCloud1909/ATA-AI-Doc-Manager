from functools import lru_cache

from pydantic import Field, field_validator, model_validator
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

    # CORS: set via env var as a comma-separated string.
    # Example: CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com
    # In production, restrict this to your specific frontend domain(s).
    cors_allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    minio_endpoint: str = "localhost:9000"
    minio_external_endpoint: str | None = None
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket: str = "documents"
    minio_presigned_expiry_minutes: int = 15
    max_upload_size_mb: int = 50

    # GCS signed-URL TTL (production).  Kept separate from MinIO so the two
    # adapters can be tuned independently without touching each other's config.
    gcs_presigned_expiry_minutes: int = 15

    default_admin_username: str = Field(default="admin", max_length=100)
    default_admin_password: str = Field(default="admin123", min_length=8)
    default_admin_role_name: str = Field(default="admin", max_length=50)
    default_user_role_name: str = Field(default="user", max_length=50)

    # Vectorization settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_batch_size: int = 20
    embedding_model: str = "gemini-embedding-2"
    llm_model: str = "gemini-2.5-flash"

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

    # GCP / Vertex AI / Cloud SQL settings (required when ENVIRONMENT=production)
    gcp_project_id: str | None = None
    gcp_location: str = "us-central1"
    gcs_bucket_name: str = "documents"
    vertex_index_id: str | None = None
    vertex_index_endpoint_id: str | None = None
    vertex_deployed_index_id: str | None = None

    # Cloud SQL (Cloud Run production only).
    # When set, db.py builds a Unix-socket URL instead of using DATABASE_URL.
    # Format: "PROJECT_ID:REGION:INSTANCE_NAME"  (e.g. "myproj:us-central1:dms-pg")
    # Leave unset (None) for local Docker Compose — DATABASE_URL is used instead.
    cloud_sql_connection_name: str | None = None
    # These are only needed when cloud_sql_connection_name is set.
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "dms_backend"

    # Cloud Tasks (production async vectorization).
    # When CLOUD_TASKS_QUEUE_NAME is set AND ENVIRONMENT=production, the
    # vectorization endpoints enqueue tasks instead of running synchronously.
    # Leave unset for local Docker Compose — synchronous mode is used instead.
    cloud_tasks_queue_name: str | None = None
    cloud_tasks_location: str = "us-central1"
    # The public URL of this Cloud Run service, used as the task target.
    # Example: "https://dms-backend-abc123-uc.a.run.app"
    worker_service_url: str | None = None
    # Service account email that Cloud Tasks will use to generate OIDC tokens.
    # Must have roles/run.invoker on this Cloud Run service.
    cloud_run_sa_email: str | None = None

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> list[str]:
        """Accept a comma-separated string or a JSON list from the environment."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Enforce strong JWT secret in production to prevent auth compromise."""
        _WEAK_DEFAULTS = {"change-me", "change-me-in-real-environments", ""}
        if self.environment.lower() in {"production", "prod"}:
            if self.jwt_secret_key in _WEAK_DEFAULTS or len(self.jwt_secret_key) < 32:
                raise ValueError(
                    "JWT_SECRET_KEY must be a strong, unique secret of at least 32 characters "
                    "when ENVIRONMENT=production. "
                    "Set the JWT_SECRET_KEY environment variable to a secure random string."
                )
        return self

    @property
    def google_ai_api_key(self) -> str | None:
        """Alias for google_api_key for backward compatibility."""
        return self.google_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
