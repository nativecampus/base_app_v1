# Architecture

## Overview

This is a FastAPI application using async SQLAlchemy with PostgreSQL. It follows a layered architecture: routers handle HTTP, services contain business logic, models define the database schema.

## Project Structure

```
app/
├── main.py              # FastAPI app, middleware, router registration
├── config.py            # Pydantic settings from environment variables
├── database.py          # Async SQLAlchemy engine and session management
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
├── static/css/          # Tailwind input and compiled CSS, custom styles
└── templates/           # Jinja2 HTML templates
alembic/                 # Database migrations
scripts/                 # Utility scripts (db reset, seeding)
tests/                   # Pytest test suite
docs/                    # Project documentation
```

## Async Pattern

All database access is async via `asyncpg`. HTTP handlers use `async def`. The database dependency (`get_db`) yields an `AsyncSession`.

Background workers running in a separate process create their own engine via `worker_session()` because each process has its own event loop.

## Background Jobs

Two modes, selected by the `REDIS_URL` environment variable:

1. **REDIS_URL empty** (default for development): jobs run in-process via FastAPI `BackgroundTasks`
2. **REDIS_URL set**: jobs are enqueued to Redis via RQ and executed by a separate worker process

The pattern for adding a new background job:

1. Write an async job runner in a service module
2. Add a sync wrapper in `app/tasks.py` that calls `asyncio.run(runner(...))`
3. In the router, check `get_queue()`: if a queue exists, enqueue the task; otherwise use `BackgroundTasks`

## Audit Trail

All models that inherit `AuditMixin` get `created_at`, `updated_at`, `created_by`, `updated_by` columns. The `created_by`/`updated_by` values are set automatically from a `ContextVar` that the HTTP middleware populates per request.

## Key Decisions

- **Async SQLAlchemy over sync**: consistent with FastAPI's async model, avoids blocking the event loop on DB calls
- **Pipenv over Poetry**: simpler for Heroku deployment
- **Tailwind CSS v4**: utility-first CSS with a small custom component layer for consistency
- **Optional Redis**: keeps development simple (no Redis required) while supporting production job queues
