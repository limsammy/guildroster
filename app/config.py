import os
import pathlib
from functools import lru_cache

from pydantic import BaseSettings, PostgresDsn, Field
from typing import Optional

class Settings(BaseSettings):
    # Common settings
    APP_NAME: str = "GuildRoster"
    ENV: str = Field("dev", env="ENV")
    SECRET_KEY: str = Field("supersecret", env="SECRET_KEY")

    # Database settings
    POSTGRES_USER: str = Field("guildroster", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("password", env="POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = Field("localhost", env="POSTGRES_SERVER")
    POSTGRES_PORT: str = Field("5432", env="POSTGRES_PORT")
    POSTGRES_DB: str = Field("guildroster", env="POSTGRES_DB")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

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