import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.core.db import get_effective_async_database_url
from app.main import app


@pytest.fixture(autouse=True)
def disable_secret_manager(monkeypatch):
    """Keep production-settings tests isolated from Google Cloud credentials."""

    def use_default(_secret_id, *, settings=None, env_var=None, default=None):
        del settings, env_var
        return default

    monkeypatch.setattr("app.shared.secret_provider.get_secret", use_default)


def test_get_effective_async_database_url_local():
    settings = Settings(
        environment="local",
        async_database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/dms_backend",
        cloud_sql_connection_name=None,
    )
    url = get_effective_async_database_url(settings)
    assert url == "postgresql+asyncpg://postgres:postgres@localhost:5432/dms_backend"


def test_get_effective_async_database_url_cloud_sql():
    settings = Settings(
        environment="production",
        db_user="dms_user",
        db_password="secret_password",
        db_name="dms_prod",
        cloud_sql_connection_name="myproj:us-central1:dms-pg",
        jwt_secret_key="a" * 32, # Keep validation happy
    )
    url = get_effective_async_database_url(settings)
    assert url == (
        "postgresql+asyncpg://dms_user:secret_password@/dms_prod"
        "?host=/cloudsql/myproj:us-central1:dms-pg"
    )


def test_production_settings_validation_invalid_local_db():
    # Unset Cloud SQL connection name but environment is production, with local db url
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            environment="production",
            database_url="postgresql+psycopg://postgres:postgres@localhost:5432/dms_backend",
            async_database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/dms_backend",
            jwt_secret_key="a" * 32,
            cloud_sql_connection_name=None,
        )
    assert "DATABASE_URL cannot point to localhost/127.0.0.1 in production" in str(exc_info.value)


def test_production_settings_validation_invalid_local_async_db():
    # Unset Cloud SQL connection name but environment is production, database_url is remote but async_database_url is local
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            environment="production",
            database_url="postgresql+psycopg://postgres:postgres@10.0.0.1:5432/dms_backend",
            async_database_url="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/dms_backend",
            jwt_secret_key="a" * 32,
            cloud_sql_connection_name=None,
        )
    assert "ASYNC_DATABASE_URL cannot point to localhost/127.0.0.1 in production" in str(exc_info.value)


def test_production_settings_validation_valid_remote_db():
    settings = Settings(
        environment="production",
        database_url="postgresql+psycopg://postgres:postgres@10.0.0.1:5432/dms_backend",
        async_database_url="postgresql+asyncpg://postgres:postgres@10.0.0.1:5432/dms_backend",
        jwt_secret_key="a" * 32,
        cloud_sql_connection_name=None,
    )
    assert settings.database_url == "postgresql+psycopg://postgres:postgres@10.0.0.1:5432/dms_backend"
    assert settings.async_database_url == "postgresql+asyncpg://postgres:postgres@10.0.0.1:5432/dms_backend"


@patch("app.main.ping_database")
@patch("app.modules.qa.api.router.chat_service")
def test_ready_endpoint_success(mock_chat_service, mock_ping):
    # Setup mocks
    mock_ping.return_value = None

    mock_connect = MagicMock()
    mock_connection = MagicMock()
    mock_connection.execute = AsyncMock()
    mock_connect.__aenter__.return_value = mock_connection
    mock_chat_service.session_service.db_engine.connect.return_value = mock_connect

    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {
            "database": "ok",
            "chat_database": "ok"
        }
    }


@patch("app.main.ping_database")
@patch("app.modules.qa.api.router.chat_service")
def test_ready_endpoint_sync_fail(mock_chat_service, mock_ping):
    from sqlalchemy.exc import OperationalError
    # Sync DB ping raises exception
    mock_ping.side_effect = OperationalError("statement", {}, Exception("Connection refused"))

    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "Sync database is not ready"


@patch("app.main.ping_database")
@patch("app.modules.qa.api.router.chat_service")
def test_ready_endpoint_async_fail(mock_chat_service, mock_ping):
    # Setup mocks
    mock_ping.return_value = None

    # Async DB ping raises exception
    mock_connect = MagicMock()
    mock_connect.__aenter__.side_effect = RuntimeError("Async DB connection failed")
    mock_chat_service.session_service.db_engine.connect.return_value = mock_connect

    client = TestClient(app)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "Async database is not ready"
