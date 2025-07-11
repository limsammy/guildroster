from fastapi import FastAPI
from app.utils.logger import get_logger


def create_app() -> FastAPI:
    logger = get_logger(__name__)
    logger.info("Starting GuildRoster API")
    app = FastAPI()
    # Add routers, middleware, config, etc. here as needed
    return app
