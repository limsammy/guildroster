import pytest
from app.config import Settings

@pytest.mark.usefixtures("monkeypatch")
def test_default_settings():
    settings = Settings()
    assert settings.APP_NAME == "GuildRoster"
    assert settings.ENV == "dev"
    assert settings.POSTGRES_USER == "guildroster"
    assert settings.POSTGRES_DB == "guildroster"
    assert "postgresql://" in settings.SQLALCHEMY_DATABASE_URI


def test_test_environment(monkeypatch):
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("POSTGRES_DB", "guildroster")
    settings = Settings()
    assert settings.ENV == "test"
    assert settings.POSTGRES_DB.endswith("_test")
    assert "guildroster_test" in settings.SQLALCHEMY_DATABASE_URI


def test_prod_environment(monkeypatch):
    monkeypatch.setenv("ENV", "prod")
    monkeypatch.setenv("POSTGRES_DB", "guildroster_prod")
    settings = Settings()
    assert settings.ENV == "prod"
    assert settings.POSTGRES_DB == "guildroster_prod"
    assert "guildroster_prod" in settings.SQLALCHEMY_DATABASE_URI


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "customuser")
    monkeypatch.setenv("POSTGRES_PASSWORD", "custompass")
    monkeypatch.setenv("POSTGRES_SERVER", "db.example.com")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("POSTGRES_DB", "customdb")
    settings = Settings()
    assert settings.POSTGRES_USER == "customuser"
    assert settings.POSTGRES_PASSWORD == "custompass"
    assert settings.POSTGRES_SERVER == "db.example.com"
    assert settings.POSTGRES_PORT == "5433"
    assert settings.POSTGRES_DB == "customdb"
    assert settings.SQLALCHEMY_DATABASE_URI == (
        "postgresql://customuser:custompass@db.example.com:5433/customdb"
    ) 