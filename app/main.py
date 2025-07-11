from fastapi import FastAPI
from app.utils.logger import get_logger
from app.database import Base, engine
from contextlib import asynccontextmanager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created (if not already present)")
    yield
    # (Optional) Add shutdown logic here


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "message": "GuildRoster API is running"}
