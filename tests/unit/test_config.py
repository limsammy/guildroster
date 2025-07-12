import os
import pytest
from app.config import Settings
from dotenv import load_dotenv


def create_dummy_env(tmp_path, env_vars):
    env_path = tmp_path / ".env"
    with open(env_path, "w") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")
    return env_path


def test_default_settings(tmp_path):
    env_vars = {
        "APP_NAME": "TestApp",
        "APP_DESCRIPTION": "Test Description",
        "VERSION": "1.2.3",
        "ENV": "dev",
        "SECRET_KEY": "dummykey",
        "DB_USER": "dummyuser",
        "DB_PASSWORD": "dummypw",
        "DB_HOST": "dummyhost",
        "DB_PORT": "1234",
        "DB_NAME": "dummydb",
    }
    env_path = create_dummy_env(tmp_path, env_vars)
    load_dotenv(dotenv_path=env_path, override=True)
    settings = Settings()
    assert settings.APP_NAME == "TestApp"
    assert settings.APP_DESCRIPTION == "Test Description"
    assert settings.VERSION == "1.2.3"
    assert settings.ENV == "dev"
    assert settings.DB_USER == "dummyuser"
    assert settings.DB_PASSWORD == "dummypw"
    assert settings.DB_HOST == "dummyhost"
    assert settings.DB_PORT == "1234"
    assert settings.DB_NAME == "dummydb"
    assert (
        "postgresql://dummyuser:dummypw@dummyhost:1234/dummydb"
        in settings.SQLALCHEMY_DATABASE_URI
    )


def test_env_vars_are_loaded(tmp_path):
    env_vars = {
        "APP_NAME": "EnvTestApp",
        "APP_DESCRIPTION": "Env Test Desc",
        "VERSION": "9.9.9",
        "ENV": "test",
        "SECRET_KEY": "envkey",
        "DB_USER": "envuser",
        "DB_PASSWORD": "envpw",
        "DB_HOST": "envhost",
        "DB_PORT": "9999",
        "DB_NAME": "envdb",
    }
    env_path = create_dummy_env(tmp_path, env_vars)
    load_dotenv(dotenv_path=env_path, override=True)
    settings = Settings()
    for k, v in env_vars.items():
        if hasattr(settings, k):
            assert getattr(settings, k) == v
    assert settings.SQLALCHEMY_DATABASE_URI == (
        "postgresql://envuser:envpw@envhost:9999/envdb"
    )
