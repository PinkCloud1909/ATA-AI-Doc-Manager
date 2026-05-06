"""
core/config.py
Đọc toàn bộ config từ biến môi trường (Cloud Run inject qua Secret Manager).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = "Runbook Platform API"
    APP_ENV:  str = "development"          # development | production
    DEBUG:    bool = False

    # ── Google Cloud ──────────────────────────────────────────────────────────
    GCP_PROJECT_ID:  str
    GCP_REGION:      str = "asia-southeast1"

    # ── Cloud SQL (PostgreSQL) ─────────────────────────────────────────────────
    # Format: "project:region:instance"
    CLOUD_SQL_INSTANCE: str = ""
    DB_USER:     str = "runbook"
    DB_PASSWORD: str = ""
    DB_NAME:     str = "runbook_db"
    # Local dev: dùng DATABASE_URL trực tiếp
    DATABASE_URL: str = "postgresql+asyncpg://runbook:runbook@localhost:5432/runbook_db"

    # ── Firebase ──────────────────────────────────────────────────────────────
    FIREBASE_PROJECT_ID: str = ""          # dùng để verify ID Token

    # ── Vertex AI ─────────────────────────────────────────────────────────────
    VERTEX_AI_LOCATION:         str = "asia-southeast1"
    GEMINI_MODEL:               str = "gemini-1.5-pro"
    GEMINI_MODEL_FLASH:         str = "gemini-1.5-flash"   # dùng cho task nhỏ

    # Vertex AI Vector Search
    VECTOR_SEARCH_INDEX_ID:      str = ""  # Index resource ID
    VECTOR_SEARCH_INDEX_ENDPOINT: str = "" # Deployed Index Endpoint ID
    VECTOR_SEARCH_TOP_K:         int = 5   # số kết quả trả về
    VECTOR_SEARCH_DISTANCE_THRESHOLD: float = 0.7  # cosine distance cutoff

    # ── GCS ───────────────────────────────────────────────────────────────────
    GCS_BUCKET_NAME:     str = "runbook-documents"
    GCS_SIGNED_URL_TTL:  int = 900          # 15 phút

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://*.run.app",
    ]

    # ── Chat ──────────────────────────────────────────────────────────────────
    CHAT_MAX_HISTORY_TURNS: int = 10       # số lượt hội thoại giữ trong context
    CHAT_STREAM_CHUNK_DELAY: float = 0.0   # giây delay giữa chunks (0 = tắt)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
