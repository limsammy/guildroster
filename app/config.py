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
    VERSION: str = "1.7.0"
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

    # Feature flags
    ENABLE_ATTENDANCE_EXPORT: bool = True

    # CORS settings
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

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
                    # Handle boolean values from .env file
                    if isinstance(getattr(self, key), bool):
                        object.__setattr__(
                            self,
                            key,
                            value.lower() in ("true", "1", "yes", "on"),
                        )
                    else:
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

    @property
    def CORS_ORIGINS_LIST(self) -> list[str]:
        """
        Parse CORS origins from comma-separated string to list.
        """
        if not self.CORS_ORIGINS:
            return []
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def CORS_ALLOW_METHODS_LIST(self) -> list[str]:
        """
        Parse CORS methods from comma-separated string to list.
        """
        if self.CORS_ALLOW_METHODS == "*":
            return ["*"]
        if not self.CORS_ALLOW_METHODS:
            return ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        return [
            method.strip()
            for method in self.CORS_ALLOW_METHODS.split(",")
            if method.strip()
        ]

    @property
    def CORS_ALLOW_HEADERS_LIST(self) -> list[str]:
        """
        Parse CORS headers from comma-separated string to list.
        """
        if self.CORS_ALLOW_HEADERS == "*":
            return ["*"]
        if not self.CORS_ALLOW_HEADERS:
            return ["*"]
        return [
            header.strip()
            for header in self.CORS_ALLOW_HEADERS.split(",")
            if header.strip()
        ]


settings = Settings()
