import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    Handles environment-specific configuration for database and secrets.
    """

    APP_NAME: str = "GuildRoster"
    APP_DESCRIPTION: str = (
        "GuildRoster is a tool for managing your guild's roster and tracking attendance."
    )
    VERSION: str = "0.1.0"
    ENV: str = "dev"
    SECRET_KEY: str = "supersecret"
    DB_USER: str = "guildroster"
    DB_PASSWORD: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "guildroster"

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
