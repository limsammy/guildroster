import os
import pathlib
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Common settings
    APP_NAME: str = "GuildRoster"
    ENV: str = "dev"
    SECRET_KEY: str = "supersecret"

    # Database settings
    POSTGRES_USER: str = "guildroster"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "guildroster"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    def __init__(self, **values):
        super().__init__(**values)
        if self.ENV == "test":
            self.POSTGRES_DB = f"{self.POSTGRES_DB}_test"
        elif self.ENV == "prod":
            # Use production DB name or override via env
            self.POSTGRES_DB = os.getenv("POSTGRES_DB", self.POSTGRES_DB)
        self.SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}" \
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()