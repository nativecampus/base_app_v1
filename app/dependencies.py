from fastapi import Request

from app.config import settings


class AuthRequired(Exception):
    """Raised when a request requires authentication but no session user exists."""
    pass


def require_auth(request: Request):
    """Return the authenticated user dict, or raise AuthRequired.

    When AUTH_ENABLED is false, returns a stub dict using CURRENT_USER.
    When AUTH_ENABLED is true, reads the user from the session cookie.
    """
    if not settings.AUTH_ENABLED:
        return {"name": settings.CURRENT_USER, "email": ""}
    user = request.session.get("user")
    if not user:
        raise AuthRequired()
    return user
