from app.config import settings


def test_settings_loads_defaults():
    assert settings.APP_NAME is not None
    assert settings.DATABASE_URL.startswith("postgresql")


def test_redis_url_defaults_to_empty():
    assert settings.REDIS_URL == ""


def test_auth0_settings_exist():
    """Auth0 config fields exist with empty defaults."""
    assert hasattr(settings, "AUTH0_DOMAIN")
    assert hasattr(settings, "AUTH0_CLIENT_ID")
    assert hasattr(settings, "AUTH0_CLIENT_SECRET")
    assert hasattr(settings, "AUTH0_SECRET_KEY")
    assert settings.AUTH0_DOMAIN == ""
    assert settings.AUTH0_CLIENT_ID == ""
    assert settings.AUTH0_CLIENT_SECRET == ""
    assert settings.AUTH0_SECRET_KEY == ""
