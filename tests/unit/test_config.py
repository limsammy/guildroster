from app.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.APP_NAME == "GuildRoster"
    assert (
        settings.APP_DESCRIPTION
        == "GuildRoster is a tool for managing your guild's roster and tracking attendance."
    )
    assert settings.VERSION == "0.1.0"
    assert settings.ENV == "dev"
    assert settings.SECRET_KEY == "supersecret"
    assert settings.DB_USER == "guildroster"
    assert settings.DB_PASSWORD == "password"
    assert settings.DB_HOST == "localhost"
    assert settings.DB_PORT == "5432"
    assert settings.DB_NAME == "guildroster_test"
    assert settings.SQLALCHEMY_DATABASE_URI == (
        "postgresql://guildroster:password@localhost:5432/guildroster_test"
    )
