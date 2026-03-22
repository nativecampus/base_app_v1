# Coding Standards

## Project Conventions

- Async everywhere: all database access, HTTP handlers, and service functions use `async/await`
- Models inherit `AuditMixin` for audit columns
- Business logic lives in `app/services/`, not in routers
- Routers handle HTTP concerns: parsing requests, returning responses, status codes
- Pydantic schemas for all request/response validation
- Enums in `app/enums.py`, not string literals

## Naming

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Database tables: `snake_case` (plural)
- Database columns: `snake_case`

## Error Handling

- Raise `HTTPException` in routers for client errors (404, 409, 422)
- Use `logging.getLogger(__name__)` in services
- Log exceptions with `logger.exception()` for stack traces
- Return structured error results from service functions, don't let exceptions propagate to routers

## Database

- Use `Depends(get_db)` in routers for session injection
- Use `selectinload` for eager loading relationships
- Commit in the service layer, not in routers
- Use Alembic for all schema changes — never modify tables manually

## Templates

- Extend `base.html` for all pages
- Use `{{ static_url('...') }}` for cache-busted static file references
- Set `active_nav` context variable for navigation highlighting

## Tests

- See docs/testing-guide.md for full guidance
- Test files mirror the module they test: `app/routers/pages.py` → `tests/test_pages.py`
- Use factory fixtures (`make_*`) to create test data
