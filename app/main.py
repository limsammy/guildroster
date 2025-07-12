from fastapi import FastAPI
from app.utils.logger import get_logger
from app.database import Base, engine
from contextlib import asynccontextmanager

from app.config import settings

logger = get_logger(__name__)

logger.info(
    f"Starting {settings.APP_NAME} v{settings.VERSION} in {settings.ENV} environment"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created (if not already present)")
    yield
    # (Optional) Add shutdown logic here


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)
logger.info(f"Created {settings.APP_NAME} v{settings.VERSION} app instance")


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"status": "ok", "message": "GuildRoster API is running"}
