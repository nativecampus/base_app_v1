# Testing Guide

## What to Test

- **Behaviour, not implementation**: test externally observable outputs
- **Public interfaces**: inputs and outputs of service functions and route handlers
- **Edge cases**: nulls, empty collections, boundaries where code makes decisions
- **State transitions and error paths**: correct exceptions, meaningful error messages
- **Conditional rendering**: if code decides whether to show something, test the condition
- **Derived display state**: formatting, computed values

## What Not to Test

- Framework code (FastAPI routing mechanics, SQLAlchemy query building)
- Private methods
- Trivial getters/setters
- Static markup or styling
- Third-party library internals

## Stack Guidance

### FastAPI
- Use the async `TestClient` via httpx
- Test status codes and response shape, not JSON parsing details
- Override dependencies via `app.dependency_overrides`

### Pydantic
- Test custom validators only
- Don't test that Pydantic validates types — that's Pydantic's job

### SQLAlchemy
- Integration test against a real database — don't mock the ORM
- Test database uses `test:test@localhost:5432/base_app_test`
- Schema is created fresh per test session via `Base.metadata.create_all`

### Alembic
- Test upgrade/downgrade reversibility when adding migrations

### Jinja2
- Test that routes pass correct context variables
- Don't test static markup

## Test Organisation

```
tests/
├── conftest.py          # Fixtures: db session, client, factories
├── test_health.py       # Health endpoint
├── test_config.py       # Configuration parsing
├── test_pages.py        # Page routes
├── test_database.py     # Database connection
└── ...                  # One file per module being tested
```

## Fixtures

The `conftest.py` provides:

- `_setup_db` (autouse, session-scoped): creates/drops all tables
- `db`: async session with rollback after each test
- `client`: `httpx.AsyncClient` with dependency overrides

Add `make_*` factory fixtures as you add models. Each factory should accept keyword overrides for all fields.

## Running Tests

```bash
pipenv run python -m pytest          # Default: coverage, max 3 failures
pipenv run python -m pytest -v       # Verbose
pipenv run python -m pytest -k name  # Filter by name
```
