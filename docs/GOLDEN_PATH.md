# Golden Path

This is the recommended path to go from clone to first real feature using this boilerplate.

## Outcome

By the end, you will:

- run the API locally in the dev container,
- understand the service-first architecture,
- implement a feature end-to-end with tests and docs,
- keep quality gates green.

## Step 1: Boot and validate

```bash
make bootstrap
make dev
```

Then check:

- `GET /ping`
- `GET /api/v1/healthz`
- `http://localhost:8000/docs`

## Step 2: Read only what you need

1. `SCOPE.md` (what this template is and is not)
2. `PROJECT_STRUCTURE.md` (where to code)
3. `DEVELOPMENT.md` (how to add resources)

## Step 3: Build your first feature

Use this sequence:

1. Add/update DB model in `app/db/models/`.
2. Create migration with `make migration-create MESSAGE="..."`.
3. Add request/response schemas in `app/api/schemas/v1/`.
4. Add business logic in `app/api/services/`.
5. Add endpoint in `app/api/endpoints/v1/`.
6. Register route in `app/api/endpoints/v1/__init__.py`.
7. Add tests in `tests/unit/` (service + endpoint success/error paths).
8. Update `docs/API.md` and any relevant docs.

## Step 4: Validate quality

```bash
make test
make all-checks
```

## Step 5: Shareable API contract

Use envelope-based responses for all API handlers and keep `dev_code` values stable. This allows frontend/mobile clients to rely on predictable success/error parsing.

## Starter client examples

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: demo-golden-path" \
  -d '{"name":"Golden Path Project","description":"Created from cURL"}'
```

### TypeScript fetch

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
