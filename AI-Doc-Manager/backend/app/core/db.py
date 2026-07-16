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

    - Local / Docker Compose: returns ``settings.resolved_database_url`` as-is.
    - Cloud Run (production): when ``CLOUD_SQL_CONNECTION_NAME`` is set, builds a
      Unix-socket URL for the Cloud SQL Auth Proxy v2 sidecar, which exposes the
      instance at ``/cloudsql/<CONNECTION_NAME>``.

    The socket path is embedded in the ``host`` query parameter rather than the
    netloc because that is what both ``psycopg`` (v3) and ``psycopg2`` require
    for Unix-socket connections.  Example resulting URL::

        postgresql+psycopg://dms_user:secret@/dms_backend
            ?host=/cloudsql/myproj:us-central1:dms-pg

    In production, ``db_user`` and ``db_password`` are resolved from Secret
    Manager via the ``resolved_db_password`` property.
    """
    if settings.cloud_sql_connection_name:
        socket_dir = f"/cloudsql/{settings.cloud_sql_connection_name}"
        return (
            f"postgresql+psycopg://"
            f"{settings.db_user}:{settings.resolved_db_password}"
            f"@/{settings.db_name}"
            f"?host={socket_dir}"
        )
    return settings.resolved_database_url


def get_effective_async_database_url(settings: Settings) -> str:
    """Return the correct asynchronous database URL for the runtime environment.

    - Local / Docker Compose: returns ``settings.resolved_async_database_url`` as-is.
    - Cloud Run (production): when ``CLOUD_SQL_CONNECTION_NAME`` is set, builds a
      Unix-socket URL for the Cloud SQL Auth Proxy v2 sidecar.

    **Note for asyncpg**: asyncpg does NOT support Unix sockets via ``?host=``.
    Use ``get_async_engine_kwargs()`` which employs the Cloud SQL Python
    Connector for async connections in production.  This function is retained
    for the sync engine path only.

    Example resulting URL (sync only):

        postgresql+psycopg://dms_user:secret@/dms_backend
            ?host=/cloudsql/myproj:us-central1:dms-pg
    """
    if settings.cloud_sql_connection_name:
        socket_dir = f"/cloudsql/{settings.cloud_sql_connection_name}"
        return (
            f"postgresql+asyncpg://"
            f"{settings.db_user}:{settings.resolved_db_password}"
            f"@/{settings.db_name}"
            f"?host={socket_dir}"
        )
    return settings.resolved_async_database_url



@lru_cache
def get_engine():
    settings = get_settings()
    return create_engine(
        _effective_database_url(settings),
        future=True,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=2,
        pool_recycle=1800,
        pool_timeout=30,
        connect_args={
            # Server-side safety: prevent runaway queries and leaked
            # transactions from consuming connections indefinitely.
            # 30 s statement timeout protects against unbounded query
            # execution; 60 s idle-in-transaction timeout detects
            # transactions that were opened but never committed/rolled
            # back (e.g. a request handler that raised mid-transaction).
            "options": (
                "-c statement_timeout=30000 "
                "-c idle_in_transaction_session_timeout=60000"
            ),
            # TCP keepalive detects dead connections (e.g. Cloud SQL
            # maintenance restart) within ~80 s instead of the OS
            # default of ~2 hours.
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
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


def get_async_engine_kwargs(settings: Settings | None = None) -> tuple[str, dict]:
    """Return ``(db_url, engine_kwargs)`` for creating an async SQLAlchemy engine.

    In local mode (``CLOUD_SQL_CONNECTION_NAME`` not set), returns the raw
    ``async_database_url`` with no extra kwargs.

    In Cloud Run production with Cloud SQL, returns an asyncpg URL plus
    ``connect_args`` that point asyncpg at the mounted Cloud SQL Unix socket.
    """
    s = settings or get_settings()

    if not s.cloud_sql_connection_name:
        return get_effective_async_database_url(s), {}

    # Cloud SQL Unix-socket connection for asyncpg.
    # The socket path is passed via connect_args["host"] which asyncpg
    # interprets as a Unix-socket directory when it starts with "/".
    #
    # We do NOT use the Cloud SQL Python Connector here because the ADK
    # DatabaseSessionService creates an async engine (create_async_engine),
    # and the Connector's connect_async event-loop requirement conflicts
    # with SQLAlchemy's internal async management.
    _socket_dir = f"/cloudsql/{s.cloud_sql_connection_name}"
    return (
        f"postgresql+asyncpg://"
        f"{s.db_user}:{s.resolved_db_password}"
        f"@/{s.db_name}",
        {"connect_args": {"host": _socket_dir}},
    )


def create_adk_session_service(
    settings: Settings | None = None,
) -> "DatabaseSessionService":
    """Return a ``DatabaseSessionService`` wired for the current environment.

    In production with Cloud SQL, the service uses the Cloud SQL Unix socket
    mounted by Cloud Run.
    """
    from google.adk.sessions import DatabaseSessionService  # noqa: PLC0415

    db_url, kwargs = get_async_engine_kwargs(settings)
    return DatabaseSessionService(db_url=db_url, **kwargs)


# Import domain models for SQLAlchemy metadata registration. Alembic relies on
# `Base.metadata` containing every mapped model when autogenerating migrations.
from app.modules import model_registry as _model_registry  # noqa: E402,F401
