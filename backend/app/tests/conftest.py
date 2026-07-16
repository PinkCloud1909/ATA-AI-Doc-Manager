import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db_session
from app.main import app
from app.modules.iam.application.seed import seed_iam_data


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)

    with testing_session_factory() as session:
        seed_iam_data(session)
        session.commit()

    def override_get_db_session():
        session = testing_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.state.session_factory = testing_session_factory

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    app.state.session_factory = None
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(client):
    session_factory = app.state.session_factory
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
