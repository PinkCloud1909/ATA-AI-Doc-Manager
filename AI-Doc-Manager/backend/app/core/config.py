from functools import lru_cache
from typing import Any

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

    # CORS: set via env var as a comma-separated string or JSON list.
    # Example: CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com
    # In production, restrict this to your specific frontend domain(s).
    #
    # Uses ``Any`` type hint instead of ``list[str]`` because pydantic-settings
    # tries to JSON-decode collection-typed fields BEFORE the field_validator
    # runs, causing a JSONDecodeError on comma-separated values like
    # "https://example.com".  With ``Any``, pydantic-settings passes the raw
    # string to the field_validator which handles both formats.
    cors_allowed_origins: Any = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
    )

    max_upload_size_mb: int = 50

    # GCS signed-URL TTL.  Used in both local dev and production.
    gcs_presigned_expiry_minutes: int = 15

    default_admin_username: str = Field(default="admin", max_length=100)
    default_admin_password: str = Field(default="admin123", min_length=8)
    default_admin_role_name: str = Field(default="admin", max_length=50)
    default_user_role_name: str = Field(default="user", max_length=50)

    # LLM model for ADK agents (QA chat, runbook generation)
    llm_model: str = "gemini-2.5-flash"

    # GCP / Cloud Storage (required for all environments — local dev uses ADC)
    gcp_project_id: str | None = None
    gcp_location: str = "us-central1"
    gcs_bucket_name: str = "documents"

    # Cloud SQL (Cloud Run production only).
    # When set, db.py builds a Unix-socket URL instead of using DATABASE_URL.
    # Format: "PROJECT_ID:REGION:INSTANCE_NAME"  (e.g. "myproj:us-central1:dms-pg")
    # Leave unset (None) for local Docker Compose — DATABASE_URL is used instead.
    cloud_sql_connection_name: str | None = None
    # When True, the Cloud SQL Python Connector uses the instance's private IP
    # (VPC-peered) instead of the public IP.  Requires the Cloud Run service to
    # have a VPC connector or direct VPC access.
    cloud_sql_use_private_ip: bool = False
    # These are only needed when cloud_sql_connection_name is set.
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "dms_backend"

    # Cloud Tasks (production async RAG ingestion).
    # When CLOUD_TASKS_QUEUE_NAME is set AND ENVIRONMENT=production, the
    # RAG ingestion endpoints enqueue tasks instead of running synchronously.
    # Leave unset for local Docker Compose — synchronous mode is used instead.
    cloud_tasks_queue_name: str | None = None
    cloud_tasks_location: str = "us-central1"
    # The public URL of this Cloud Run service, used as the task target.
    # Example: "https://dms-backend-abc123-uc.a.run.app"
    worker_service_url: str | None = None
    # Service account email that Cloud Tasks will use to generate OIDC tokens.
    # Must have roles/run.invoker on this Cloud Run service.
    cloud_run_sa_email: str | None = None

    # ── RAG Engine (Vertex AI managed RAG) ───────────────────────────
    # Full RAG corpus resource name.  Auto-created on first use when empty.
    # Format: projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{CORPUS_ID}
    rag_corpus_resource: str | None = None
    # RAG Engine location.  When empty, falls back to GCP_LOCATION.
    # Must be us-central1 for serverless mode.
    rag_engine_location: str = ""
    # Embedding model for the RAG corpus.  Fixed at corpus creation.
    rag_embedding_model: str = "text-embedding-005"
    # Chunking settings for RAG Engine import (server-side).
    # The layout-parser docs recommend 1024/256 for Document AI.
    rag_chunk_size: int = 1024
    rag_chunk_overlap: int = 256
    # Enable Document AI Layout Parser for improved PDF/DOCX chunking.
    rag_layout_parser_enabled: bool = False
    # Document AI Layout Parser processor resource name (required when enabled).
    # Format: projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}
    # Example: projects/my-project/locations/us/processors/abc123def456
    rag_layout_parser_processor_name: str | None = None
    # Max parsing requests per minute for the layout parser.
    rag_layout_parser_max_parsing_rpm: int = 120
    # Optional LLM model for parsing images / scanned documents.
    # Example: "gemini-2.5-flash".  Leave empty for the default parser.
    rag_llm_parser_model: str | None = None
    # Max embedding RPM during import (1–1500).  Default: 1000.
    rag_max_embedding_requests_per_min: int = 1000
    # Cosine distance threshold for retrieval (0–2).  Only chunks with
    # distance below this value are returned.  Lower = stricter matching.
    # Default 0.5 is a reasonable starting point per the official docs.
    rag_retrieval_distance_threshold: float = 0.5
    # Maximum time (seconds) to wait for an import_files() call to complete.
    # Default 600 (10 min).  Large files may need more time.
    rag_import_timeout_seconds: int = 600
    # Optional GCS prefix for per-file import result NDJSON files.
    # A unique suffix (document-id + uuid) is appended per import so the
    # object name is always unique when the import API requires it.
    rag_import_result_sink: str | None = None

    @property
    def resolved_rag_engine_location(self) -> str:
        """Effective RAG Engine region — RAG_ENGINE_LOCATION if set, else GCP_LOCATION."""
        return self.rag_engine_location or self.gcp_location

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> list[str]:
        """Accept a comma-separated string or a JSON list from the environment."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Enforce strong JWT secret and remote database config in production."""
        _WEAK_DEFAULTS = {"change-me", "change-me-in-real-environments", ""}
        if self.environment.lower() in {"production", "prod"}:
            resolved_jwt = self.resolved_jwt_secret_key
            if resolved_jwt in _WEAK_DEFAULTS or len(resolved_jwt) < 32:
                raise ValueError(
                    "JWT_SECRET_KEY must be a strong, unique secret of at least 32 characters "
                    "when ENVIRONMENT=production. "
                    "Set the JWT_SECRET_KEY environment variable to a secure random string."
                )
            if not self.cloud_sql_connection_name:
                for name, url in [
                    ("DATABASE_URL", self.database_url),
                    ("ASYNC_DATABASE_URL", self.async_database_url),
                ]:
                    if "localhost" in url or "127.0.0.1" in url:
                        raise ValueError(
                            f"{name} cannot point to localhost/127.0.0.1 in production. "
                            "Provide a real database host or configure CLOUD_SQL_CONNECTION_NAME to use Cloud SQL sockets."
                        )
        return self

    # ------------------------------------------------------------------
    # Secret Manager resolution for production
    # ------------------------------------------------------------------
    # In production critical secrets (JWT key, DB creds, API key) should be
    # stored in Secret Manager, not environment variables.  The properties
    # below try Secret Manager first when ENVIRONMENT=production, then fall
    # back to the env-var value already on the Settings instance.
    #
    # IMPORTANT: These properties are read lazily.  The pydantic-settings
    # model MUST still have valid defaults so that the application can
    # bootstrap and read the secret manager at all.

    @property
    def resolved_jwt_secret_key(self) -> str:
        """JWT secret, resolved from Secret Manager in production."""
        from app.shared.secret_provider import get_secret  # noqa: PLC0415
        return get_secret(
            "jwt-secret-key",
            settings=self,
            default=self.jwt_secret_key,
        )

    @property
    def resolved_database_url(self) -> str:
        """Sync database URL, resolved from Secret Manager in production."""
        from app.shared.secret_provider import get_secret  # noqa: PLC0415
        return get_secret(
            "database-url",
            settings=self,
            default=self.database_url,
        )

    @property
    def resolved_async_database_url(self) -> str:
        """Async database URL, resolved from Secret Manager in production."""
        from app.shared.secret_provider import get_secret  # noqa: PLC0415
        return get_secret(
            "async-database-url",
            settings=self,
            default=self.async_database_url,
        )

    @property
    def resolved_db_password(self) -> str:
        """Database password, resolved from Secret Manager in production."""
        from app.shared.secret_provider import get_secret  # noqa: PLC0415
        return get_secret(
            "db-password",
            settings=self,
            default=self.db_password,
        )

    @property
    def resolved_google_api_key(self) -> str | None:
        """Google API key, resolved from Secret Manager in production."""
        from app.shared.secret_provider import get_secret  # noqa: PLC0415
        return get_secret(
            "google-api-key",
            settings=self,
            default=self.google_api_key,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
