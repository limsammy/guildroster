from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# SQLAlchemy engine
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True, future=True)

# SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes (if needed)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

