# type: ignore[comparison-overlap,assignment]
import pytest
from sqlalchemy.orm import Session
from app import database
from app.config import settings


def test_engine_uri():
    # SQLAlchemy censors the password in the URL string
    expected_uri = settings.SQLALCHEMY_DATABASE_URI.replace(
        settings.DB_PASSWORD, "***"
    )
    assert str(database.engine.url) == expected_uri


def test_sessionlocal_produces_session():
    session = database.SessionLocal()
    try:
        assert isinstance(session, Session)
    finally:
        session.close()


def test_base_is_declarative_base():
    # Declarative base classes have a metadata attribute
    assert hasattr(database.Base, "metadata")


def test_get_db_yields_session():
    gen = database.get_db()
    session = next(gen)
    assert isinstance(session, Session)
    with pytest.raises(StopIteration):
        next(gen)
