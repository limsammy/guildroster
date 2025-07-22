from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import logging

# Add debug logging for DB connection
logging.basicConfig(level=logging.INFO)
logging.info(f"Connecting to DB: {settings.SQLALCHEMY_DATABASE_URI}")
logging.info(f"DB_USER: {settings.DB_USER}")
logging.info(f"DB_PASSWORD: {settings.DB_PASSWORD}")
logging.info(f"DB_HOST: {settings.DB_HOST}")
logging.info(f"DB_PORT: {settings.DB_PORT}")
logging.info(f"DB_NAME: {settings.DB_NAME}")

# SQLAlchemy engine for database connections
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, echo=False, future=True
)

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
