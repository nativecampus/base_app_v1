# Architecture

## Overview

This is a FastAPI application using async SQLAlchemy with PostgreSQL. It follows a layered architecture: routers handle HTTP, services contain business logic, models define the database schema.

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
│   ├── __init__.py      # Re-exports Base and AuditMixin
│   └── base.py          # DeclarativeBase, AuditMixin, audit event listeners
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic layer
├── routers/             # HTTP endpoint handlers
│   ├── auth.py          # Auth0 login/callback/logout (when AUTH_ENABLED)
│   └── pages.py         # HTML page routes
├── static/css/          # Tailwind input and compiled CSS, custom styles
└── templates/           # Jinja2 HTML templates
alembic/                 # Database migrations
scripts/                 # Utility scripts (db reset, seeding)
tests/                   # Pytest test suite
docs/                    # Project documentation
```

## Async Pattern

All database access is async via `asyncpg`. HTTP handlers use `async def`. The database dependency (`get_db`) yields an `AsyncSession`.

Background workers running in a separate process create their own engine via `worker_session()` because each process has its own event loop. The worker engine is lazily created and reused across tasks within the same process.

## Authentication

Auth0 via authlib, session-based. Controlled by the `AUTH_ENABLED` environment variable.

When `AUTH_ENABLED=false` (default): no auth routes are registered, `CURRENT_USER` is used as the identity for audit columns, and `require_auth` returns a stub user dict.

When `AUTH_ENABLED=true`: the auth router is included (`/auth/login`, `/auth/callback`, `/auth/logout`), `SessionMiddleware` signs cookies with `AUTH0_SECRET_KEY`, and `require_auth` reads the user from the session or raises `AuthRequired` (which redirects to `/auth/login`).

The `require_auth` dependency (`app/dependencies.py`) is used to protect routes:

```python
from fastapi import Depends
from app.dependencies import require_auth

@router.get("/protected")
async def protected(user: dict = Depends(require_auth)):
    ...
```

### Audit Trail Bridge

The HTTP middleware reads the authenticated user from the session and sets a `ContextVar`. The `AuditMixin` columns (`created_by`, `updated_by`) pick up this value automatically. When auth is enabled, email is preferred; falls back to name, then to `CURRENT_USER`.

## Background Jobs

Two modes, selected by the `REDIS_URL` environment variable:

1. **REDIS_URL empty** (default for development): jobs run in-process via FastAPI `BackgroundTasks`
2. **REDIS_URL set**: jobs are enqueued to Redis via RQ and executed by a separate worker process

The pattern for adding a new background job:

1. Write an async job runner in a service module
2. Add a sync wrapper in `app/tasks.py` that calls `asyncio.run(runner(...))`
3. In the router, check `get_queue()`: if a queue exists, enqueue the task; otherwise use `BackgroundTasks`

## Audit Trail

All models that inherit `AuditMixin` get `created_at`, `updated_at`, `created_by`, `updated_by` columns. The `created_by`/`updated_by` values are set automatically from a `ContextVar` that the HTTP middleware populates per request. When authentication is enabled, the middleware reads the user identity from the Auth0 session.

## Key Decisions

- **Async SQLAlchemy over sync**: consistent with FastAPI's async model, avoids blocking the event loop on DB calls
- **Pipenv over Poetry**: simpler for Heroku deployment
- **Tailwind CSS v4**: utility-first CSS with a small custom component layer for consistency
- **Optional Redis**: keeps development simple (no Redis required) while supporting production job queues
- **Auth0 via authlib**: session-based OAuth flow, toggled by AUTH_ENABLED
