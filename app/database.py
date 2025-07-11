from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# SQLAlchemy engine for database connections
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True, future=True)

# Factory for creating new database sessions
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, future=True
)

# Declarative base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a SQLAlchemy session.
    Yields:
        Session: SQLAlchemy database session.
    Ensures session is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
