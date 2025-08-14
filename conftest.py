import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from fastapi.testclient import TestClient
from app.config import settings

# Use the test database URI
TEST_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# Create a new engine and session for tests
engine = create_engine(TEST_DATABASE_URL, echo=False, future=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, future=True
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Drop and recreate all tables at the start of the test session
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Optionally drop tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Clean the database between tests by deleting all data."""
    yield
    # Create a fresh session for cleanup
    cleanup_session = TestingSessionLocal()
    try:
        # Delete all data from all tables
        for table in reversed(Base.metadata.sorted_tables):
            cleanup_session.execute(table.delete())
        cleanup_session.commit()
    except Exception:
        cleanup_session.rollback()
    finally:
        cleanup_session.close()


@pytest.fixture(scope="function")
def client(db_session):
    # Dependency override for get_db
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides = {}
    from app import database

    app.dependency_overrides[database.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
