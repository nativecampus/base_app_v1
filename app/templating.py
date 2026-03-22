import hashlib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_templates_dir = Path(__file__).parent / "templates"
_static_dir = Path(__file__).parent / "static"

env = Environment(loader=FileSystemLoader(str(_templates_dir)), autoescape=True)


def _file_hash(path: Path) -> str:
    """Return a short hash of a file for cache-busting."""
    if path.exists():
        return hashlib.md5(path.read_bytes()).hexdigest()[:8]
    return "0"


def static_url(filename: str) -> str:
    """Return a cache-busted static URL."""
    path = _static_dir / filename
    return f"/static/{filename}?v={_file_hash(path)}"


def initials(name: str) -> str:
    """Return uppercase initials from a name."""
    parts = name.strip().split()
    return "".join(p[0] for p in parts[:2]).upper() if parts else "?"


def avatar_color(name: str) -> str:
    """Return a deterministic hex colour from a name."""
    colors = [
        "#ef4444", "#f97316", "#eab308", "#22c55e",
        "#14b8a6", "#3b82f6", "#8b5cf6", "#ec4899",
    ]
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(colors)
    return colors[idx]


env.globals["static_url"] = static_url
env.globals["initials"] = initials
env.globals["avatar_color"] = avatar_color
