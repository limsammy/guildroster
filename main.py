from typing import Union

from fastapi import FastAPI

from app import create_app
from app.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Starting GuildRoster API")

app = create_app()
