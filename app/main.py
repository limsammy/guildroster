from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import get_logger
from app.database import Base, engine
from contextlib import asynccontextmanager

from app.config import settings
from app.models.token import Token
from app.utils.auth import require_any_token, security

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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    from app.routers import (
        user,
        token,
        guild,
        team,
        member,
        toon,
        raid,
        scenario,
        attendance,
    )

    app.include_router(user.router)
    app.include_router(token.router)
    app.include_router(guild.router)
    app.include_router(team.router)
    app.include_router(member.router)
    app.include_router(toon.router)
    app.include_router(raid.router)
    app.include_router(scenario.router)
    app.include_router(attendance.router)

    @app.get("/", dependencies=[Depends(security)])
    def read_root(current_token: Token = Depends(require_any_token)):
        """Health check endpoint."""
        return {"status": "ok", "message": "GuildRoster API is running"}

    return app


app = create_app()
logger.info(f"Created {settings.APP_NAME} v{settings.VERSION} app instance")
