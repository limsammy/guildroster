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

    # App settings
    APP_NAME: str = "GuildRoster"
    APP_DESCRIPTION: str = (
        "GuildRoster is a tool for managing your guild's roster and tracking attendance."
    )
    VERSION: str = "0.1.0"
    ENV: str = "dev"
    SECRET_KEY: str = "supersecret"

    # Database settings
    DB_USER: str = "guildroster"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "guildroster"

    # WarcraftLogs API settings
    WARCRAFTLOGS_CLIENT_ID: str = ""
    WARCRAFTLOGS_CLIENT_SECRET: str = ""
    WARCRAFTLOGS_API_URL: str = "https://www.warcraftlogs.com/api/v2/client"
    WARCRAFTLOGS_TOKEN_URL: str = "https://www.warcraftlogs.com/oauth/token"

    def __init__(self, **values):
        super().__init__(**values)
        # Load environment variables from .env file
        env_file = (
            ".env.test" if "PYTEST_CURRENT_TEST" in os.environ else ".env"
        )
        try:
            config = dotenv_values(env_file)
            # Override defaults with values from .env file
            for key, value in config.items():
                if hasattr(self, key):
                    object.__setattr__(self, key, value)
        except FileNotFoundError:
            # .env file doesn't exist, use defaults
            pass

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
