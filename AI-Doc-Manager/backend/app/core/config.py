from functools import lru_cache
import os
from pathlib import Path

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

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    gcp_project_id: str | None = None
    gcp_region: str | None = None
    gcs_bucket: str = "documents"
    gcs_signed_url_expiry_minutes: int = 15

    vertex_ai_location: str | None = None
    vertex_ai_endpoint: str | None = None
    vertex_ai_index_endpoint_id: str | None = None
    vertex_ai_index_id: str | None = None

    use_cloud_sql_connector: bool = False
    cloud_sql_connection_name: str | None = None
    cloud_sql_db_user: str | None = None
    cloud_sql_db_password: str | None = None
    cloud_sql_db_name: str | None = None

    default_admin_username: str = Field(default="admin", max_length=100)
    default_admin_password: str = Field(default="admin123", min_length=8)
    default_admin_role_name: str = Field(default="admin", max_length=50)
    default_user_role_name: str = Field(default="user", max_length=50)


@lru_cache
def get_settings() -> Settings:
    return Settings()
