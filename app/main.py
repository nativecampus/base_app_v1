from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models.base import set_current_user, _current_user_var
from app.routers import pages

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.middleware("http")
async def set_audit_user(request: Request, call_next):
    """Populate the audit context var with the configured user for each request."""
    token = set_current_user(settings.CURRENT_USER)
    try:
        response = await call_next(request)
    finally:
        _current_user_var.reset(token)
    return response


app.include_router(pages.router)


@app.get("/health")
async def health():
    """Return a simple health check response."""
    return {"status": "healthy"}
