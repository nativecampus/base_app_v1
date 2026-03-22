from unittest.mock import patch


async def test_audit_user_middleware_uses_settings(client):
    """Middleware should read CURRENT_USER from settings, not os.getenv."""
    with patch("app.main.settings") as mock_settings:
        mock_settings.CURRENT_USER = "from-settings"
        mock_settings.APP_NAME = "test"
        mock_settings.APP_VERSION = "0"
        captured = []
        original_set = __import__("app.models.base", fromlist=["set_current_user"]).set_current_user

        def spy(user):
            captured.append(user)
            return original_set(user)

        with patch("app.main.set_current_user", side_effect=spy):
            await client.get("/health")

    assert captured == ["from-settings"]
