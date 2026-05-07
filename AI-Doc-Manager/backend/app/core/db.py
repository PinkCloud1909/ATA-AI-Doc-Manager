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


from app.modules import model_registry as _model_registry  # noqa: E402,F401
