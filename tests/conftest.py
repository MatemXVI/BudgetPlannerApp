import os
# Ensure the app uses an in-memory DB during tests to avoid touching local files
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# IMPORTANT: import app and Base after setting up test engine/overrides
from app.database import Base
from app.main import app
from app.database import get_db

# Create a dedicated in-memory SQLite engine shared across connections
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(scope="session", autouse=True)
def create_test_db_schema():
    """Create all tables once for the in-memory database."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture()
def db_session():
    """Provide a SQLAlchemy session bound to a SAVEPOINT, rolled back after each test."""
    connection = TEST_ENGINE.connect()
    txn = connection.begin()
    session = TestSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        txn.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient with DB dependency overridden to use the test session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
