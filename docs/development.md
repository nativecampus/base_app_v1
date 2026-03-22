# Development

## Prerequisites

- Python 3.12
- PostgreSQL 16
- Node.js (for Tailwind CSS compilation)
- pipenv

## Initial Project Setup (from template)

```bash
curl -sL https://raw.githubusercontent.com/nativecampus/base_app/main/install.sh | bash -s your_project_name
```

This clones the repo, renames all references, creates databases, installs dependencies, runs migrations, and builds CSS.

To run the scaffolding step separately (e.g. if you already cloned manually):

```bash
pipenv run python -m scripts.init_project your_project_name
```

Pass `--yes` to skip the database creation prompt.

## Setup

```bash
pipenv install --dev && npm install && pipenv run alembic upgrade head && npm run build:css
```

## Running

Development server with auto-reload:

```bash
pipenv run uvicorn app.main:app --reload --port 8000
```

CSS watcher (separate terminal):

```bash
npm run watch:css
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

Create test database (once):

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
