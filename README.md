# Base App

Project template for internal Python web applications.

## What You Get

- **Async FastAPI** web application with Jinja2 templates and Tailwind CSS v4
- **PostgreSQL** with async SQLAlchemy, Alembic migrations, and an audit trail (created_at, updated_at, created_by, updated_by on every model)
- **Background jobs** via Redis + RQ in production, with automatic in-process fallback for development (no Redis required locally)
- **Testing** with pytest, pytest-asyncio, and a real database — no mocks
- **CI** via GitHub Actions with PostgreSQL service container
- **Heroku deployment** via Procfile
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

This clones the template, renames everything to your project name, installs dependencies, creates databases, runs migrations, builds CSS, and makes an initial git commit.

Then:

```bash
cd my_new_app
```

```bash
python manage.py dev
```

Your app is running at `http://localhost:8000`.

## Next Steps

Add your models in `app/models/`, schemas in `app/schemas/`, services in `app/services/`, routes in `app/routers/`, and generate your first migration:

```bash
pipenv run alembic revision --autogenerate -m "initial tables"
```

See the `docs/` directory for architecture, coding standards, and testing guidance.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web framework | FastAPI (async) |
| Database | PostgreSQL + async SQLAlchemy + Alembic |
| Templates | Jinja2 + Tailwind CSS v4 |
| Background jobs | Redis + RQ (optional — falls back to in-process) |
| Testing | pytest + pytest-asyncio |
| Deployment | Heroku (Procfile) |

## Contributing

See [docs/development.md](docs/development.md) for setup and development workflow.
