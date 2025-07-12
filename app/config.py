from typing import ClassVar
from pydantic_settings import BaseSettings

# Load environment variables from .env file
from dotenv import dotenv_values
import os


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

    DB_USER: str = config.get("DB_USER") or "guildroster"
    DB_PASSWORD: str = config.get("DB_PASSWORD") or "password"
    DB_HOST: str = config.get("DB_HOST") or "localhost"
    DB_PORT: str = config.get("DB_PORT") or "5432"
    DB_NAME: str = config.get("DB_NAME") or "guildroster"

    def __init__(self, **values):
        super().__init__(**values)
        # Automatic test DB switching
        if "PYTEST_CURRENT_TEST" in os.environ:
            object.__setattr__(self, "DB_NAME", f"{self.DB_NAME}_test")

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
