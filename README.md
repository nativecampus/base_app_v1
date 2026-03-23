# Base App

A project template for Python web applications. Run one command to scaffold a new project with authentication, background jobs, an audit trail, and production deployment — ready to build on.

## What's Included

- **Async FastAPI** with Jinja2 templates and Tailwind CSS v4
- **PostgreSQL** with async SQLAlchemy, Alembic migrations, and automatic audit columns (`created_at`, `updated_at`, `created_by`, `updated_by`) on every model
- **Auth0 authentication** (opt-in) with session-based login, route protection, and audit trail integration
- **Background jobs** via Redis + RQ in production, with automatic in-process fallback for development
- **CI** via GitHub Actions with a PostgreSQL service container
- **Heroku deployment** via Procfile with web, worker, and release processes
- **[Claude Wizard](https://github.com/nativecampus/claude-wizard)** skill for disciplined, test-driven development with Claude Code
- **Project management CLI** (`manage.py`) for setup, dev server, and CSS building
- **Documentation** covering architecture, coding standards, data model, API reference, and testing conventions

## Prerequisites

- Python 3.12
- PostgreSQL 16
- Node.js (for Tailwind CSS)
- pipenv

## Create a New Project

```bash
curl -sL https://raw.githubusercontent.com/nativecampus/base_app_v1/main/install.sh | bash -s my_new_app
```

This:

1. Clones the template and renames all references to your project name
2. Installs Python and npm dependencies
3. Creates the main and test databases
4. Runs Alembic migrations
5. Builds Tailwind CSS
6. Installs the Claude Wizard skill
7. Makes an initial git commit

Then:

```bash
cd my_new_app
```

```bash
python manage.py dev
```

Your app is running at `http://localhost:8000`.

## Post-Scaffolding Checklist

After creating your project:

1. Create a GitHub repository and push your initial commit
2. Copy `.env.example` to `.env` and fill in your values (see [Environment Variables](#environment-variables))
3. Set up Auth0 if your app needs authentication (see [Authentication](#authentication))
4. Add your models in `app/models/`, schemas in `app/schemas/`, services in `app/services/`, routes in `app/routers/`
5. Generate your first migration:

```bash
pipenv run alembic revision --autogenerate -m "initial tables"
```

6. Review the `docs/` directory — architecture, coding standards, data model, API reference, and testing conventions are all documented there

## Authentication

Auth is disabled by default. To enable Auth0:

1. Create an Auth0 application (Regular Web Application)
2. Set the callback URL to `http://localhost:8000/auth/callback`
3. Set the logout URL to `http://localhost:8000`
4. Add the following to `.env`:

```dotenv
AUTH_ENABLED=TRUE
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_SECRET_KEY=a-random-secret-for-session-cookies
```

When enabled, unauthenticated requests to protected routes redirect to `/auth/login`. Audit trail columns (`created_by`, `updated_by`) use the authenticated user's email, falling back to name, then `CURRENT_USER`.

Protect routes with the `require_auth` dependency:

```python
from fastapi import Depends
from app.dependencies import require_auth

@router.get("/protected")
async def protected(user: dict = Depends(require_auth)):
    ...
```

## Environment Variables

Copy `.env.example` to `.env`. All variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://localhost/base_app` | PostgreSQL connection string |
| `AUTH_ENABLED` | `FALSE` | Enable Auth0 authentication |
| `AUTH0_DOMAIN` | | Auth0 tenant domain |
| `AUTH0_CLIENT_ID` | | Auth0 application client ID |
| `AUTH0_CLIENT_SECRET` | | Auth0 application client secret |
| `AUTH0_SECRET_KEY` | | Secret for signing session cookies |
| `CURRENT_USER` | `system` | Fallback identity for audit columns when auth is disabled |
| `REDIS_URL` | | Redis URL for background jobs (empty = in-process fallback) |

## manage.py Commands

| Command | Description |
|---------|-------------|
| `python manage.py dev` | Run the dev server (uvicorn + Tailwind CSS watcher) |
| `python manage.py setup` | Install deps, create databases, run migrations, build CSS |
| `python manage.py init <name>` | Initialise a new project from the template (used by `install.sh`) |

## Background Jobs

Two modes, selected by the `REDIS_URL` environment variable:

- **`REDIS_URL` empty** (default): jobs run in-process via FastAPI `BackgroundTasks`
- **`REDIS_URL` set**: jobs are enqueued to Redis via RQ and executed by a separate worker

To run the worker locally:

```bash
pipenv run rq worker --url $REDIS_URL base-app
```

macOS requires `SimpleWorker` to avoid `fork()` crashes:

```bash
pipenv run rq worker --worker-class rq.SimpleWorker --url $REDIS_URL base-app
```

## Deployment

Heroku deployment via Procfile:

- `web`: uvicorn
- `worker`: RQ worker (scale to 0 if not using Redis)
- `release`: runs `alembic upgrade head` on deploy

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI (async) |
| Database | PostgreSQL + async SQLAlchemy + Alembic |
| Templates | Jinja2 + Tailwind CSS v4 |
| Background jobs | Redis + RQ (optional — falls back to in-process) |
| Testing | pytest + pytest-asyncio |
| Deployment | Heroku (Procfile) |
| Auth | Auth0 via authlib (opt-in) |
| AI tooling | Claude Wizard skill |

## Contributing

See [docs/development.md](docs/development.md) for working on base_app itself.

## Licence

[MIT](LICENSE)
