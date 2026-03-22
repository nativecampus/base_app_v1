# API Reference

## Health Check

```
GET /health
→ {"status": "healthy"}
```

## Authentication (when AUTH_ENABLED=true)

```
GET /auth/login     → Redirects to Auth0 login page
GET /auth/callback  → Auth0 callback, stores user in session, redirects to /
GET /auth/logout    → Clears session, redirects to Auth0 logout
```

Unauthenticated requests to protected routes return `307` redirect to `/auth/login`.

## Pages

```
GET /  → HTML index page
```

## Adding Endpoints

When adding new endpoints, document them here with:

- Method and path
- Query parameters (with defaults)
- Request body schema (if applicable)
- Response schema
- Status codes and error conditions
