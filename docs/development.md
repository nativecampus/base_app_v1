# Development

## Prerequisites

- Python 3.12
- PostgreSQL 16
- Node.js (for Tailwind CSS compilation)
- pipenv

## Initial Project Setup (from template)

```bash
python manage.py init your_project_name
```

This renames all references, installs dependencies, creates databases, runs migrations, and builds CSS.

## Setup

```bash
python manage.py setup
```

This installs dependencies, creates both the main and test databases, runs migrations, and builds CSS.

## Running

Dev server with auto-reload and CSS watcher:

```bash
python manage.py dev
```

RQ worker (if using Redis):

```bash
pipenv run rq worker --url $REDIS_URL base-app
```

macOS requires SimpleWorker to avoid fork() crashes:

```bash
pipenv run rq worker --worker-class rq.SimpleWorker --url $REDIS_URL base-app
```

## Testing

The test database is created automatically by `manage.py setup` and `manage.py init`. To create it manually:

```bash
createdb -U test base_app_test
```

Run tests:

```bash
pipenv run python -m pytest
```

Verbose output:

```bash
pipenv run python -m pytest -v
```

Test database credentials: `test:test` on `localhost:5432/base_app_test`.

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

## Deployment

Heroku deployment via Procfile:

- `web`: uvicorn
- `worker`: RQ worker (scale to 0 if not using Redis)
- `release`: runs `alembic upgrade head` on deploy

Environment variables: see `.env.example`.
