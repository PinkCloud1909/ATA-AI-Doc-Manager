"""
db/session.py
Async SQLAlchemy session factory.
- Local dev: kết nối trực tiếp qua DATABASE_URL
- Cloud Run:  kết nối qua Cloud SQL Python Connector (IAM auth, không cần password)
"""
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _build_engine():
    # Cloud Run environment: dùng Cloud SQL Connector
    if settings.CLOUD_SQL_INSTANCE and settings.APP_ENV == "production":
        from google.cloud.sql.connector import AsyncConnector, IPTypes

        connector = AsyncConnector()

        async def _getconn():
            return await connector.connect(
                settings.CLOUD_SQL_INSTANCE,
                "asyncpg",
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                db=settings.DB_NAME,
                ip_type=IPTypes.PRIVATE,  # Private IP trong VPC
            )

        engine = create_async_engine(
            "postgresql+asyncpg://",
            async_creator=_getconn,
            poolclass=NullPool,   # Cloud Run: stateless, không pool
        )
    else:
        # Local dev
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=5,
            max_overflow=10,
        )

    return engine


engine = _build_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — inject DB session vào endpoint."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
