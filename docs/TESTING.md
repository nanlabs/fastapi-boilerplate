# Testing Guide

## Running tests

```bash
make test
make test-unit
make test-integration
make test-coverage
```

## Test structure

```text
tests/
├── conftest.py
├── unit/
│   ├── api/endpoints/
│   ├── core/
│   ├── schemas/
│   └── services/
└── integration/
```

## Key fixtures

| Fixture | Scope | Purpose |
|---|---|---|
| `test_engine` | session | SQLite test engine and schema setup |
| `db_session` | function | Per-test DB session with rollback |
| `client` | function | `TestClient` with DB dependency override |

## Endpoint assertion pattern

```python
resp = client.post("/api/v1/projects", json={"name": "My Project"})
assert resp.status_code == 201
body = resp.json()
assert body["success"] is True
assert body["dev_code"] == "PROJECT_CREATED"
assert body["data"]["name"] == "My Project"
assert body["metadata"]["request_id"] is not None
```

## Error assertion pattern

```python
resp = client.get("/api/v1/projects/9999")
assert resp.status_code == 404
body = resp.json()
assert body["success"] is False
assert body["dev_code"] == "NOT_FOUND"
assert body["data"] is None
```
