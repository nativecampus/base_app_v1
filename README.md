# Base App

Template for internal Python web applications.

## Quick Start

```bash
curl -sL https://raw.githubusercontent.com/nativecampus/base_app/main/install.sh | bash -s my_new_app
```

```bash
cd my_new_app
```

```bash
python manage.py dev
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI (async) |
| Database | PostgreSQL + async SQLAlchemy + Alembic |
| Templates | Jinja2 + Tailwind CSS v4 |
| Background jobs | Redis + RQ (optional — falls back to in-process) |
| Testing | pytest + pytest-asyncio |
| Deployment | Heroku (Procfile) |

## Documentation

See [CLAUDE.md](CLAUDE.md) for AI agent guidance and links to all docs.
