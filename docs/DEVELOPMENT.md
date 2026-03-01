# Development Guide

## Principles

- Keep endpoints thin and delegate business logic to services.
- Do not add endpoint-level `try/except`; rely on global exception handlers.
- Return `APIResponse[T]` from API endpoints.
- Use query dependencies (`get_pagination`, `get_sorting`, `get_search`) for list endpoints.

## Add a new resource end-to-end

1. Create DB model in `app/db/models/`.
2. Create migration (`make migration-create MESSAGE="..."`) and apply it.
3. Create schemas in `app/api/schemas/v1/`.
4. Implement service in `app/api/services/`.
5. Implement endpoint module in `app/api/endpoints/v1/`.
6. Register route in `app/api/endpoints/v1/__init__.py`.
7. Add tests in `tests/unit/` for service and endpoint behavior.
8. Update docs in `docs/API.md` and `docs/PROJECT_STRUCTURE.md` if needed.

## Recommended command sequence

```bash
make test
make all-checks
make dev
```

## Error and response conventions

- Business errors should raise custom exceptions from `app/api/exceptions.py`.
- Map errors centrally in `app/core/exception_handlers.py`.
- Use `dev_code` values that are stable and machine-readable.

## Database and environment

- Default DB: SQLite.
- Production DB: PostgreSQL via `DATABASE_URL`.
- See `docs/DATABASE.md` and `docs/CONFIGURATION.md`.
