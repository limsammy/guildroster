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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative dev port
            "http://127.0.0.1:5173",  # Alternative localhost
            "http://127.0.0.1:3000",  # Alternative localhost
            "http://localhost",  # Port 80 (default HTTP)
            "http://127.0.0.1",  # Port 80 (default HTTP)
            "http://159.223.132.130",  # Production IP (HTTP)
            "http://guildroster.io",  # Production domain (root, HTTP)
            "http://www.guildroster.io",  # Production domain (www, HTTP)
            "https://159.223.132.130",  # Production IP (HTTPS)
            "https://guildroster.io",  # Production domain (root, HTTPS)
            "https://www.guildroster.io",  # Production domain (www, HTTPS)
            "http://159.223.132.130:3000",
            "https://159.223.132.130:3000",  # HTTPS version of frontend
            "https://159.223.132.130:80",  # HTTPS on port 80
            "http://159.223.132.130:80",  # HTTP on port 80
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
