from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


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
        settings.database_url,
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


<<<<<<< Updated upstream
from app.modules import model_registry as _model_registry  # noqa: E402,F401
=======
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
>>>>>>> Stashed changes
