from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templating import env

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the home page."""
    template = env.get_template("index.html")
    return template.render(request=request, active_nav="home")
