from fastapi import FastAPI
from app.utils.logger import get_logger
from app.database import Base, engine
from contextlib import asynccontextmanager

from app.config import settings

logger = get_logger(__name__)

logger.info(
    f"Starting {settings.APP_NAME} v{settings.VERSION} in {settings.ENV} environment"
)
logger.info(
    f"Postgres user: {settings.DB_USER} password: {settings.DB_PASSWORD}"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created (if not already present)")
    yield
    # (Optional) Add shutdown logic here


def create_app() -> FastAPI:
    """App Factory to create a FastAPI app instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    # Include routers
    from app.routers import user

    app.include_router(user.router)

    @app.get("/")
    def read_root():
        """Health check endpoint."""
        return {"status": "ok", "message": "GuildRoster API is running"}

    return app


app = create_app()
logger.info(f"Created {settings.APP_NAME} v{settings.VERSION} app instance")
