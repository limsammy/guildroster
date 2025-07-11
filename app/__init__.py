"""
GuildRoster FastAPI application factory.

This module provides the create_app function to construct and configure the FastAPI app instance.
"""

from fastapi import FastAPI
from app.utils.logger import get_logger


def create_app() -> FastAPI:
    """
    Application factory for the GuildRoster FastAPI app.

    Sets up logging and returns a configured FastAPI instance.
    Add routers, middleware, and configuration as needed.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    logger = get_logger(__name__)
    logger.info("Starting GuildRoster API")
    app = FastAPI()
    # Add routers, middleware, config, etc. here as needed
    return app
