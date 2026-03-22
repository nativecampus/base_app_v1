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

Install dependencies:

```bash
pipenv install --dev && npm install
```

Create database and build CSS:

```bash
createdb base_app && pipenv run alembic upgrade head && npm run build:css
```

Run:

```bash
pipenv run uvicorn app.main:app --reload --port 8000
```

## Using as a Template

```bash
curl -sL https://raw.githubusercontent.com/nativecampus/base_app/main/install.sh | bash -s my_new_app
```

This clones the repo, renames everything, creates databases, installs dependencies, runs migrations, and builds CSS.

Then add your models in `app/models/`, schemas in `app/schemas/`, services in `app/services/`, routes in `app/routers/`, and generate your first migration with `pipenv run alembic revision --autogenerate -m "initial tables"`.

## Documentation

See [CLAUDE.md](CLAUDE.md) for AI agent guidance and links to all docs.
