import logging

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)


@router.get("/login")
async def login(request: Request):
    """Redirect to Auth0 login page."""
    callback_url = request.url_for("callback")
    return await oauth.auth0.authorize_redirect(request, str(callback_url))


@router.get("/callback")
async def callback(request: Request):
    """Handle Auth0 callback, store user in session."""
    token = await oauth.auth0.authorize_access_token(request)
    userinfo = token.get("userinfo", {})
    request.session["user"] = {
        "name": userinfo.get("name", ""),
        "email": userinfo.get("email", ""),
    }
    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    """Clear session and redirect to Auth0 logout."""
    request.session.clear()
    logout_url = (
        f"https://{settings.AUTH0_DOMAIN}/v2/logout"
        f"?client_id={settings.AUTH0_CLIENT_ID}"
        f"&returnTo={request.base_url}"
    )
    return RedirectResponse(url=logout_url, status_code=302)
