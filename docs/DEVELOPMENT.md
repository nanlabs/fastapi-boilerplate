# Development Guide

## Principles

- Keep endpoints thin and delegate business logic to services.
- Do not add endpoint-level `try/except`; rely on global exception handlers.
- Return `APIResponse[T]` from API endpoints.
- Use query dependencies (`get_pagination`, `get_sorting`, `get_search`) for list endpoints.
- Prefer test-first changes (red -> green -> refactor).

If you are new to this repository, read the "End-to-end walkthrough" section at the bottom of this guide first.

## Golden workflow for a new resource

1. Create DB model in `app/db/models/`.
2. Create migration (`make migration-create MESSAGE="..."`) and apply it.
3. Create schemas in `app/api/schemas/v1/`.
4. Implement service in `app/api/services/`.
5. Implement endpoint module in `app/api/endpoints/v1/`.
6. Register route in `app/api/endpoints/v1/__init__.py`.
7. Add tests in `tests/unit/` for service and endpoint behavior first or in parallel.
8. Update docs in `docs/API.md` and `docs/PROJECT_STRUCTURE.md` if needed.

## Recommended command sequence (local loop)

```bash
make test-unit
make autofix
make all-checks
```

Before opening a PR:

```bash
make test
make all-checks
```

For command details and alternatives, see `COMMANDS.md`.

## Error and response conventions

- Business errors should raise custom exceptions from `app/api/exceptions.py`.
- Map errors centrally in `app/core/exception_handlers.py`.
- Use `dev_code` values that are stable and machine-readable.
- Keep response messages client-friendly and consistent.

## Database and environment

- Default DB: SQLite.
- Production DB: PostgreSQL via `DATABASE_URL`.
- See `docs/DATABASE.md` and `docs/CONFIGURATION.md`.

## Definition of done for a feature

- Endpoint returns `APIResponse[T]` and includes stable `dev_code`.
- Service layer contains business logic; endpoint remains orchestration-only.
- Unit tests cover success + main error paths.
- `make test` and `make all-checks` pass.
- Documentation links and new docs are validated by `make check-docs`.
- Docs updated when API behavior or project structure changes.

## Anti-patterns to avoid

- Writing business logic directly in endpoint handlers.
- Catching broad exceptions in endpoint functions.
- Returning ad-hoc response shapes that bypass envelope helpers.
- Merging schema changes without migration review.

## End-to-end walkthrough

By following the golden workflow above you will:

- run the API locally in the Dev Container,
- understand the service-first architecture,
- implement a feature end-to-end with tests and docs,
- keep quality gates green.

### API contract note

Use envelope-based responses for all API handlers and keep `dev_code` values stable. This allows frontend/mobile clients to rely on predictable success/error parsing.

### Starter client examples

cURL:

```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: demo-dev-guide" \
  -d '{"name":"My First Project","description":"Created from cURL"}'
```

TypeScript fetch:

```typescript
type ApiResponse<T> = {
  success: boolean;
  dev_code: string;
  message: string;
  data: T | null;
  errors: Array<{ field?: string; message: string }>;
  metadata: { request_id: string; timestamp: string };
};

type Project = { id: number; name: string; description: string | null };

const response = await fetch("http://localhost:8000/api/v1/projects");
const body = (await response.json()) as ApiResponse<Project[]>;
if (!body.success) throw new Error(`${body.dev_code}: ${body.message}`);
console.log(body.data);
```

## Related docs

- `API.md` for response envelope and endpoint contract details.
- `TESTING.md` for fixture and assertion patterns.
- `COMMANDS.md` for all available `make` targets.
