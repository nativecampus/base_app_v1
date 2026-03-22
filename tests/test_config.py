from app.config import settings


def test_settings_loads_defaults():
    assert settings.APP_NAME is not None
    assert settings.DATABASE_URL.startswith("postgresql")


def test_redis_url_defaults_to_empty():
    assert settings.REDIS_URL == ""
