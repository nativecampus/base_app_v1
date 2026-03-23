# Development

## Initial Project Setup (from template)

If you want to use base_app as a template for a new project, see the [README](../README.md). This section is stripped automatically when a project is scaffolded.

To set up base_app for template development:

```bash
python manage.py setup
```

This installs dependencies, creates the `base_app` and `base_app_test` databases, runs migrations, builds CSS, and installs the Claude Wizard skill.

## Running

Dev server with auto-reload and CSS watcher:

```bash
python manage.py dev
```

## Testing

Test database credentials: `test:test` on `localhost:5432/base_app_test`.

Run tests:

```bash
pipenv run python -m pytest
```

Verbose output:

```bash
pipenv run python -m pytest -v
```

Filter by name:

```bash
pipenv run python -m pytest -k name
```

## Database Migrations

Apply all pending migrations:

```bash
pipenv run alembic upgrade head
```

Generate migration from model changes:

```bash
pipenv run alembic revision --autogenerate -m "description of change"
```

Rollback one migration:

```bash
pipenv run alembic downgrade -1
```

Show current migration state:

```bash
pipenv run alembic current
```

## Seeding

Seed all data:

```bash
pipenv run python -m scripts.seed_all
```

Seed specific data:

```bash
pipenv run python -m scripts.seed_all --only settings
```

Reset database (drops and recreates all tables):

```bash
pipenv run python -m scripts.db_reset
```

Skip confirmation:

```bash
pipenv run python -m scripts.db_reset --yes
```

## Project Structure

```
app/
├── main.py              # FastAPI app, middleware, router registration
├── config.py            # Pydantic settings from environment variables
├── database.py          # Async SQLAlchemy engine and session management
├── dependencies.py      # FastAPI dependencies (auth, etc.)
├── enums.py             # Shared enum definitions
├── worker.py            # Redis/RQ queue helpers (optional)
├── tasks.py             # Synchronous RQ task wrappers
├── templating.py        # Jinja2 environment, globals, filters
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
├── routers/             # HTTP endpoint handlers
├── static/css/          # Tailwind input and compiled CSS
└── templates/           # Jinja2 HTML templates
alembic/                 # Database migrations
scripts/                 # Utility scripts (db reset, seeding)
tests/                   # Pytest test suite
docs/                    # Project documentation
```

## RQ Worker

If using Redis for background jobs:

```bash
pipenv run rq worker --url $REDIS_URL base-app
```

macOS requires SimpleWorker to avoid fork() crashes:

```bash
pipenv run rq worker --worker-class rq.SimpleWorker --url $REDIS_URL base-app
```

## Deployment

Heroku deployment via Procfile:

- `web`: uvicorn
- `worker`: RQ worker (scale to 0 if not using Redis)
- `release`: runs `alembic upgrade head` on deploy

Environment variables: see `.env.example`.
