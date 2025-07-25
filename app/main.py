from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import get_logger
from app.utils.request_logger import RequestLoggingMiddleware
from app.database import Base, engine
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.models.token import Token
from app.utils.auth import require_any_token, security

# Configure SQLAlchemy logging to be less verbose
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)

logger = get_logger(__name__)

logger.info(
    f"Starting {settings.APP_NAME} v{settings.VERSION} in {settings.ENV} environment"
)
logger.info(f"Postgres user: {settings.DB_USER} password: [REDACTED]")


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
        # Documentation customization
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS middleware
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS_LIST}")
    logger.info(f"CORS Allow Credentials: {settings.CORS_ALLOW_CREDENTIALS}")
    logger.info(f"CORS Allow Methods: {settings.CORS_ALLOW_METHODS_LIST}")
    logger.info(f"CORS Allow Headers: {settings.CORS_ALLOW_HEADERS_LIST}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS_LIST,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS_LIST,
        allow_headers=settings.CORS_ALLOW_HEADERS_LIST,
    )

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Include routers
    from app.routers import (
        user,
        token,
        guild,
        team,
        toon,
        raid,
        scenario,
        attendance,
    )

    app.include_router(user.router)
    app.include_router(token.router)
    app.include_router(guild.router)
    app.include_router(team.router)
    app.include_router(toon.router)
    app.include_router(raid.router)
    app.include_router(scenario.router)
    app.include_router(attendance.router)

    @app.get("/")
    def read_root():
        """Health check endpoint."""
        return {"status": "ok", "message": "GuildRoster API is running"}

    return app


app = create_app()
logger.info(f"Created {settings.APP_NAME} v{settings.VERSION} app instance")
