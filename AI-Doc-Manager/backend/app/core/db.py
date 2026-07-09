from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import Settings, get_settings


class Base(DeclarativeBase):
    pass


def _effective_database_url(settings: Settings) -> str:
    """Return the correct synchronous database URL for the runtime environment.

    - Local / Docker Compose: returns ``settings.database_url`` as-is.
    - Cloud Run (production): when ``CLOUD_SQL_CONNECTION_NAME`` is set, builds a
      Unix-socket URL for the Cloud SQL Auth Proxy v2 sidecar, which exposes the
      instance at ``/cloudsql/<CONNECTION_NAME>``.

    The socket path is embedded in the ``host`` query parameter rather than the
    netloc because that is what both ``psycopg`` (v3) and ``psycopg2`` require
    for Unix-socket connections.  Example resulting URL::

        postgresql+psycopg://dms_user:secret@/dms_backend
            ?host=/cloudsql/myproj:us-central1:dms-pg

    NOTE: ``asyncpg`` uses a different parameter name (``server_settings`` or the
    ``?host=`` style from pg-bouncer) — if the async engine also needs Cloud SQL
    socket support, extend this function accordingly and open a separate session.
    """
    if settings.cloud_sql_connection_name:
        socket_dir = f"/cloudsql/{settings.cloud_sql_connection_name}"
        return (
            f"postgresql+psycopg://"
            f"{settings.db_user}:{settings.db_password}"
            f"@/{settings.db_name}"
            f"?host={socket_dir}"
        )
    return settings.database_url


@lru_cache
def get_engine():
    settings = get_settings()
    if settings.use_cloud_sql_connector:
        if not (
            settings.cloud_sql_connection_name
            and settings.cloud_sql_db_user
            and settings.cloud_sql_db_password
            and settings.cloud_sql_db_name
        ):
            raise ValueError("Cloud SQL connector settings are incomplete")
        from google.cloud.sql.connector import Connector

        connector = Connector()

        def getconn():
            return connector.connect(
                settings.cloud_sql_connection_name,
                "pg8000",
                user=settings.cloud_sql_db_user,
                password=settings.cloud_sql_db_password,
                db=settings.cloud_sql_db_name,
            )

        return create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            future=True,
            pool_pre_ping=True,
        )

    return create_engine(
        _effective_database_url(settings),
        future=True,
        pool_pre_ping=True,
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def ping_database(session: Session) -> None:
    session.execute(text("SELECT 1"))


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Import domain models for SQLAlchemy metadata registration. Alembic relies on
# `Base.metadata` containing every mapped model when autogenerating migrations.
from app.modules import model_registry as _model_registry  # noqa: E402,F401
