from unittest.mock import patch

import pytest
from fastapi import Request

from app.dependencies import require_auth, AuthRequired


def _fake_request(session_data: dict | None = None):
    """Build a minimal Request-like object with a session."""
    scope = {"type": "http", "method": "GET", "path": "/"}
    req = Request(scope)
    req.state._state = {}
    # Starlette stores session data on scope; mock it directly
    scope["session"] = session_data or {}
    return req


async def test_require_auth_disabled_returns_current_user():
    """When AUTH_ENABLED=false, require_auth returns a dict with CURRENT_USER."""
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.AUTH_ENABLED = False
        mock_settings.CURRENT_USER = "dev-user"
        result = require_auth(_fake_request())
    assert result == {"name": "dev-user", "email": ""}


async def test_require_auth_enabled_with_session_user():
    """When AUTH_ENABLED=true and session has user, return that user."""
    user = {"name": "Alice", "email": "alice@example.com"}
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.AUTH_ENABLED = True
        result = require_auth(_fake_request(session_data={"user": user}))
    assert result == user


async def test_require_auth_enabled_no_session_raises():
    """When AUTH_ENABLED=true and no session user, raise AuthRequired."""
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.AUTH_ENABLED = True
        with pytest.raises(AuthRequired):
            require_auth(_fake_request())


async def test_require_auth_enabled_empty_session_raises():
    """When AUTH_ENABLED=true and session user is empty, raise AuthRequired."""
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.AUTH_ENABLED = True
        with pytest.raises(AuthRequired):
            require_auth(_fake_request(session_data={"user": None}))
