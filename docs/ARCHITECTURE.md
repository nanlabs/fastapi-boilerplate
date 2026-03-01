# Architecture

## High-level design

The boilerplate follows a layered API architecture:

- **`endpoints/v1`**: HTTP contract for API v1 only.
- **`services`**: business logic and database interactions (not versioned).
- **`schemas/common`**: cross-version schemas (`APIResponse`, query params).
- **`schemas/v1`**: version-specific request/response models.
- **`core`**: cross-cutting concerns (middleware, logging, exception handling).

## API versioning strategy

Versioning is at the HTTP layer:

- Registered router: `app.include_router(v1_router, prefix="/api/v1")`
- Future version behavior changes should create new versioned endpoints/schemas while keeping services reusable when possible.

## Response model strategy

All success and error responses are standardized under:

- `APIResponse[T]`
- Helpers: `make_item_response`, `make_list_response`, `make_error_response`

Benefits:
- Stable client contract.
- Consistent metadata (`request_id`, `timestamp`, pagination context).
- Consistent machine-readable codes via `dev_code`.

## Error handling strategy

Endpoints avoid local `try/except`; errors are mapped centrally in `app/core/exception_handlers.py`.

Mapped examples:
- `NotFoundError` -> `404 / NOT_FOUND`
- `ConflictError` -> `409 / CONFLICT`
- `SortingValidationError` -> `400 / INVALID_SORT_FIELD`
- `RequestValidationError` -> `422 / VALIDATION_ERROR`
- `DatabaseError` -> `500 / DATABASE_ERROR`
- fallback `Exception` -> `500 / INTERNAL_ERROR`

## Observability

- Request ID middleware:
  - Reuses incoming `X-Request-ID` if provided, otherwise generates UUIDv4.
  - Exposes `request.state.request_id` and always returns `X-Request-ID`.
- Logging:
  - `DEBUG=true`: human-readable logs.
  - `DEBUG=false`: JSON logs.
