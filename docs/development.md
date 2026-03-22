# Development

## Prerequisites

- Python 3.12
- PostgreSQL 16
- Node.js (for Tailwind CSS compilation)
- pipenv

## Initial Project Setup (from template)

```bash
pipenv run python -m scripts.init_project your_project_name
```

This renames all references throughout the codebase and offers to create databases.

## Setup

```bash
pipenv install --dev
npm install
pipenv run alembic upgrade head
npm run build:css
```

## Running

```bash
# Development server with auto-reload
pipenv run uvicorn app.main:app --reload --port 8000

# CSS watcher (separate terminal)
npm run watch:css

# RQ worker (if using Redis)
pipenv run rq worker --url $REDIS_URL base-app

# macOS requires SimpleWorker to avoid fork() crashes
pipenv run rq worker --worker-class rq.SimpleWorker --url $REDIS_URL base-app
```

## Testing

```bash
# Create test database (once)
createdb -U test base_app_test

# Run tests
pipenv run python -m pytest

# With verbose output
pipenv run python -m pytest -v
```

Test database credentials: `test:test` on `localhost:5432/base_app_test`.

## Database Migrations

```bash
# Apply all pending migrations
pipenv run alembic upgrade head

# Generate migration from model changes
pipenv run alembic revision --autogenerate -m "description of change"

# Rollback one migration
pipenv run alembic downgrade -1

# Show current migration state
pipenv run alembic current
```

## Seeding

```bash
# Seed all data
pipenv run python -m scripts.seed_all

# Seed specific data
pipenv run python -m scripts.seed_all --only settings

# Reset database (drops and recreates all tables)
pipenv run python -m scripts.db_reset
pipenv run python -m scripts.db_reset --yes  # skip confirmation
```

## Deployment

Heroku deployment via Procfile:

- `web`: uvicorn
- `worker`: RQ worker (scale to 0 if not using Redis)
- `release`: runs `alembic upgrade head` on deploy

Environment variables: see `.env.example`.
