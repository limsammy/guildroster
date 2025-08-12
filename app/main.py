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
    # Check if database schema matches current models
    try:
        from sqlalchemy import inspect

        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        expected_tables = set(Base.metadata.tables.keys())

        if expected_tables - existing_tables:
            logger.warning(
                "Database schema is out of date - run 'alembic upgrade head'"
            )
        else:
            logger.info("Database schema is up to date")
    except Exception as e:
        logger.error(f"Error checking database schema: {e}")

    yield


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

    # Add request logging middleware FIRST (before CORS)
    app.add_middleware(RequestLoggingMiddleware)

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
        invite,
        import_export,
    )

    app.include_router(user.router)
    app.include_router(token.router)
    app.include_router(guild.router)
    app.include_router(team.router)
    app.include_router(toon.router)
    app.include_router(raid.router)
    app.include_router(scenario.router)
    app.include_router(attendance.router)
    app.include_router(invite.router)
    app.include_router(import_export.router)

    @app.get("/")
    def read_root():
        """Health check endpoint."""
        return {"status": "ok", "message": "GuildRoster API is running"}

    @app.get("/version")
    def get_version():
        """Get application version information."""
        import subprocess
        from datetime import datetime

        # Get git commit hash if available
        git_commit = "unknown"
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=".",
            )
            if result.returncode == 0:
                git_commit = result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return {
            "version": settings.VERSION,
            "app_name": settings.APP_NAME,
            "environment": settings.ENV,
            "build_date": datetime.utcnow().isoformat() + "Z",
            "git_commit": git_commit,
        }

    return app


app = create_app()
logger.info(f"Created {settings.APP_NAME} v{settings.VERSION} app instance")
