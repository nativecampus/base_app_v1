from unittest.mock import patch

import pytest
from fastapi import Depends, FastAPI, Request
from httpx import ASGITransport, AsyncClient
from starlette.middleware.sessions import SessionMiddleware

from app.models.base import set_current_user, _current_user_var


async def test_audit_user_middleware_uses_settings(client):
    """Middleware should read CURRENT_USER from settings, not os.getenv."""
    with patch("app.main.settings") as mock_settings:
        mock_settings.CURRENT_USER = "from-settings"
        mock_settings.AUTH_ENABLED = False
        mock_settings.APP_NAME = "test"
        mock_settings.APP_VERSION = "0"
        captured = []
        original_set = set_current_user

        def spy(user):
            captured.append(user)
            return original_set(user)

        with patch("app.main.set_current_user", side_effect=spy):
            await client.get("/health")

    assert captured == ["from-settings"]


def _build_app_with_audit_middleware(auth_enabled: bool):
    """Build a test app that captures the audit user via the real middleware."""
    app = FastAPI()

    @app.middleware("http")
    async def set_audit_user(request: Request, call_next):
        from app.config import settings as real_settings
        if auth_enabled:
            user = request.session.get("user")
            username = user.get("email") or user.get("name") if user else real_settings.CURRENT_USER
        else:
            username = real_settings.CURRENT_USER
        token = set_current_user(username)
        try:
            response = await call_next(request)
        finally:
            _current_user_var.reset(token)
        return response

    app.add_middleware(SessionMiddleware, secret_key="test-secret")

    @app.get("/whoami")
    async def whoami():
        return {"audit_user": _current_user_var.get()}

    return app


async def test_middleware_uses_session_email_when_auth_enabled():
    """When auth is enabled and session has user, audit trail uses email."""
    app = _build_app_with_audit_middleware(auth_enabled=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Set a session cookie by making a request through a helper endpoint
        @app.get("/set-session")
        async def set_session(request: Request):
            request.session["user"] = {"name": "Alice", "email": "alice@example.com"}
            return {"ok": True}

        r = await ac.get("/set-session")
        cookies = r.cookies

        response = await ac.get("/whoami", cookies=cookies)
    assert response.json()["audit_user"] == "alice@example.com"


async def test_middleware_uses_name_when_no_email():
    """When auth is enabled and session user has no email, audit trail uses name."""
    app = _build_app_with_audit_middleware(auth_enabled=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        @app.get("/set-session")
        async def set_session(request: Request):
            request.session["user"] = {"name": "Bob", "email": ""}
            return {"ok": True}

        r = await ac.get("/set-session")
        response = await ac.get("/whoami", cookies=r.cookies)
    assert response.json()["audit_user"] == "Bob"


async def test_middleware_falls_back_to_current_user_when_no_session():
    """When auth is enabled but no session user, falls back to CURRENT_USER."""
    app = _build_app_with_audit_middleware(auth_enabled=True)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/whoami")
    assert response.json()["audit_user"] == "test"
