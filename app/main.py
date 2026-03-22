import secrets

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.dependencies import AuthRequired
from app.models.base import set_current_user, _current_user_var
from app.routers import pages

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.middleware("http")
async def set_audit_user(request: Request, call_next):
    """Populate the audit context var from the session user or CURRENT_USER."""
    if settings.AUTH_ENABLED:
        user = request.session.get("user")
        username = user.get("email") or user.get("name") if user else settings.CURRENT_USER
    else:
        username = settings.CURRENT_USER
    token = set_current_user(username)
    try:
        response = await call_next(request)
    finally:
        _current_user_var.reset(token)
    return response


# SessionMiddleware must be added after the HTTP middleware above so it wraps
# around it (Starlette processes the outermost middleware first).
session_secret = settings.AUTH0_SECRET_KEY or secrets.token_hex(32)
app.add_middleware(SessionMiddleware, secret_key=session_secret)


@app.exception_handler(AuthRequired)
async def auth_required_handler(request: Request, exc: AuthRequired):
    """Redirect unauthenticated requests to the login page."""
    return RedirectResponse(url="/auth/login", status_code=307)


if settings.AUTH_ENABLED:
    if not settings.AUTH0_SECRET_KEY:
        raise RuntimeError("AUTH0_SECRET_KEY must be set when AUTH_ENABLED=true")
    from app.routers import auth
    app.include_router(auth.router)

app.include_router(pages.router)


@app.get("/health")
async def health():
    """Return a simple health check response."""
    return {"status": "healthy"}
