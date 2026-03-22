from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from httpx import ASGITransport, AsyncClient
from starlette.middleware.sessions import SessionMiddleware

from app.dependencies import AuthRequired


def _require_auth_enabled(request: Request):
    """require_auth with AUTH_ENABLED=true behaviour."""
    user = request.session.get("user")
    if not user:
        raise AuthRequired()
    return user


def _build_auth_app():
    """Build a minimal FastAPI app with auth enabled for testing."""
    from app.routers import auth

    test_app = FastAPI()

    @test_app.exception_handler(AuthRequired)
    async def _handler(request: Request, exc: AuthRequired):
        return RedirectResponse(url="/auth/login", status_code=307)

    test_app.include_router(auth.router)

    @test_app.get("/")
    async def index(request: Request, user: dict = Depends(_require_auth_enabled)):
        return {"user": user}

    test_app.add_middleware(SessionMiddleware, secret_key="test-secret-long-enough-for-testing")
    return test_app


@pytest.fixture
def auth_app():
    return _build_auth_app()


async def test_login_redirects_to_auth0(auth_app):
    """GET /auth/login should redirect to Auth0."""
    with patch("app.routers.auth.oauth") as mock_oauth:
        mock_client = MagicMock()
        mock_client.authorize_redirect = AsyncMock(
            return_value=RedirectResponse(url="https://test.auth0.com/authorize", status_code=302)
        )
        mock_oauth.auth0 = mock_client

        transport = ASGITransport(app=auth_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/auth/login", follow_redirects=False)
    assert response.status_code == 302


async def test_logout_clears_session_and_redirects(auth_app):
    """GET /auth/logout should redirect to Auth0 logout endpoint."""
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 302
    location = response.headers["location"]
    assert "logout" in location


async def test_callback_stores_user_in_session(auth_app):
    """GET /auth/callback should store user info and redirect to /."""
    with patch("app.routers.auth.oauth") as mock_oauth:
        mock_client = MagicMock()
        mock_client.authorize_access_token = AsyncMock(return_value={
            "userinfo": {"name": "Alice", "email": "alice@example.com"}
        })
        mock_oauth.auth0 = mock_client

        transport = ASGITransport(app=auth_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/auth/callback", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/"


async def test_unauthenticated_request_redirects_to_login(auth_app):
    """Protected route without session user redirects to /auth/login."""
    transport = ASGITransport(app=auth_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/auth/login" in response.headers["location"]
