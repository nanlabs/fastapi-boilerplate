# API

## Base URL and versioning

- Development: `http://localhost:8000`
- Version prefix: `/api/v1`

## Health endpoints

- `GET /ping`: infrastructure probe, no envelope.
  - Response: `{ "status": "ok" }`
- `GET /api/v1/healthz`: API client health check, with envelope.

## Standard response envelope

All API responses (success and errors) use:

```json
{
  "success": true,
  "status_code": 200,
  "dev_code": "PROJECTS_LISTED",
  "message": "Projects retrieved successfully",
  "data": [],
  "errors": [],
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-03-01T10:00:00Z",
    "pagination": { "skip": 0, "limit": 100, "total": 42 },
    "sort": { "sort_by": "created_at", "sort_direction": "desc" },
    "search": { "search": null }
  }
}
```

Validation error example (`422`):

```json
{
  "success": false,
  "status_code": 422,
  "dev_code": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "data": null,
  "errors": [
    { "field": "name", "message": "String should have at least 1 character" }
  ],
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-03-01T10:00:00Z"
  }
}
```

## `dev_code` reference

| Situation | `dev_code` |
|---|---|
| List success | `PROJECTS_LISTED` |
| Retrieve success | `PROJECT_RETRIEVED` |
| Create success | `PROJECT_CREATED` |
| Update success | `PROJECT_UPDATED` |
| Delete success | `PROJECT_DELETED` |
| Not found | `NOT_FOUND` |
| Conflict | `CONFLICT` |
| Invalid sort field | `INVALID_SORT_FIELD` |
| Request validation | `VALIDATION_ERROR` |
| Database failure | `DATABASE_ERROR` |
| Unexpected failure | `INTERNAL_ERROR` |

## Projects endpoints

### `GET /api/v1/projects`

Query params:
- `skip` (default `0`)
- `limit` (default `100`, max `1000`)
- `sort_by`
- `sort_direction` (`asc` or `desc`)
- `search`

Returns envelope with `metadata.pagination.total`.

### `POST /api/v1/projects`

Request body:

```json
{
  "name": "New Project",
  "description": "Project description"
}
```

Response: `201` envelope with `dev_code: PROJECT_CREATED`.

### `GET /api/v1/projects/{project_id}`

Response: `200` envelope with `dev_code: PROJECT_RETRIEVED`, or `404` envelope with `dev_code: NOT_FOUND`.

### `PATCH /api/v1/projects/{project_id}`

Partial update endpoint. Response: `200` envelope with `dev_code: PROJECT_UPDATED`.

### `DELETE /api/v1/projects/{project_id}`

Response is `200` envelope (not `204`) with:

```json
{
  "success": true,
  "dev_code": "PROJECT_DELETED",
  "data": null
}
```

## OpenAPI

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Client integration examples

### cURL

```bash
curl -X GET "http://localhost:8000/api/v1/projects" \
  -H "Accept: application/json" \
  -H "X-Request-ID: api-docs-example"
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

async function listProjects(): Promise<void> {
  const resp = await fetch("http://localhost:8000/api/v1/projects");
  const body = (await resp.json()) as ApiResponse<Array<{ id: number; name: string }>>;
  if (!body.success) throw new Error(`${body.dev_code}: ${body.message}`);
  console.log(body.data);
}
```
