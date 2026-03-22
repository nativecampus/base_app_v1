# Base App

Template for internal Python web applications. Clone this repo as the starting point for new projects.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI (async) |
| Database | PostgreSQL + async SQLAlchemy + Alembic |
| Templates | Jinja2 + Tailwind CSS v4 |
| Background jobs | Redis + RQ (optional — falls back to in-process) |
| Testing | pytest + pytest-asyncio |
| Deployment | Heroku (Procfile) |

## Quick Start

```bash
python manage.py setup
```

This installs dependencies, creates the database, runs migrations, and builds CSS.

```bash
python manage.py dev
```

This starts uvicorn with auto-reload and the CSS watcher.

## Using as a Template

Clone and reset history:

```bash
git clone git@github.com:nativecampus/base_app.git my_new_app && cd my_new_app && rm -rf .git && git init
```

Initialise the project (renames everything, installs deps, creates databases, runs migrations, builds CSS):

```bash
python manage.py init my_new_app
```

Then add your models in `app/models/`, schemas in `app/schemas/`, services in `app/services/`, routes in `app/routers/`, and generate your first migration with `pipenv run alembic revision --autogenerate -m "initial tables"`.

## Documentation

See [CLAUDE.md](CLAUDE.md) for AI agent guidance and links to all docs.
