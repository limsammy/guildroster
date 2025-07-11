import pytest
from app.config import Settings


def test_default_settings():
    settings = Settings()
    assert settings.APP_NAME == "GuildRoster"
    assert settings.ENV == "dev"
    assert settings.DB_USER == "guildroster"
    assert settings.DB_NAME == "guildroster"
    assert "postgresql://" in settings.SQLALCHEMY_DATABASE_URI
    assert settings.APP_METADATA["title"] == settings.APP_NAME
    assert settings.APP_METADATA["description"] == settings.APP_DESCRIPTION
    assert settings.APP_METADATA["version"] == settings.VERSION


def test_test_environment(monkeypatch):
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("DB_NAME", "guildroster")
    settings = Settings()
    assert settings.ENV == "test"
    assert settings.DB_NAME is not None and settings.DB_NAME.endswith("_test")
    assert "guildroster_test" in settings.SQLALCHEMY_DATABASE_URI


def test_prod_environment(monkeypatch):
    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setenv("DB_NAME", "guildroster_prod")
    settings = Settings()
    assert settings.ENV == "prod"
    assert settings.DB_NAME == "guildroster_prod"
    assert "guildroster_prod" in settings.SQLALCHEMY_DATABASE_URI


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("DB_USER", "customuser")
    monkeypatch.setenv("DB_PASSWORD", "custompass")
    monkeypatch.setenv("DB_HOST", "db.example.com")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "customdb")
    settings = Settings()
    assert settings.DB_USER == "customuser"
    assert settings.DB_PASSWORD == "custompass"
    assert settings.DB_HOST == "db.example.com"
    assert settings.DB_PORT == "5433"
    assert settings.DB_NAME == "customdb"
    assert settings.SQLALCHEMY_DATABASE_URI == (
        "postgresql://customuser:custompass@db.example.com:5433/customdb"
    )
