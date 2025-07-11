import os
from typing import ClassVar
from pydantic_settings import BaseSettings

# Load environment variables from .env file
from dotenv import dotenv_values


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    Handles environment-specific configuration for database and secrets.
    """

    # Load environment variables from .env file
    config: ClassVar = dotenv_values(".env")

    # App settings
    APP_NAME: str = config.get("APP_NAME") or "GuildRoster"
    APP_DESCRIPTION: str = (
        config.get("APP_DESCRIPTION")
        or "GuildRoster is a tool for managing your guild's roster and tracking attendance."
    )
    VERSION: str = config.get("VERSION") or "0.1.0"
    ENV: str = config.get("ENV") or "dev"
    SECRET_KEY: str = config.get("SECRET_KEY") or "supersecret"

    # Database settings
    DB_USER: str = config.get("DB_USER") or "guildroster"
    DB_PASSWORD: str = config.get("DB_PASSWORD") or "password"
    DB_HOST: str = config.get("DB_HOST") or "localhost"
    DB_PORT: str = config.get("DB_PORT") or "5432"
    DB_NAME: str = config.get("DB_NAME") or "guildroster"

    def __init__(self, **values):
        """
        Initialize settings and adjust database name for test/prod environments.
        """
        super().__init__(**values)
        if self.ENV == "test":
            self.DB_NAME = f"{self.DB_NAME}_test"
        elif self.ENV == "prod":
            # Use production DB name or override via env
            self.DB_NAME = os.getenv("DB_NAME", self.DB_NAME)

    # Metadata dictionary for FastAPI settings
    @property
    def APP_METADATA(self) -> dict:
        """
        Metadata dictionary for FastAPI settings.
        """
        return {
            "title": self.APP_NAME,
            "description": self.APP_DESCRIPTION,
            "version": self.VERSION,
        }

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Construct the SQLAlchemy database URI from current settings.
        """
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
