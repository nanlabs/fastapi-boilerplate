# Getting Started

## Prerequisite

Use the Dev Container workflow for development.

## Setup

1. Open the project and choose **Reopen in Container**, or run:

```bash
devcontainer up --workspace-folder .
```

2. In the container terminal, run:

```bash
make install-dev
make init-db
```

3. Start the API:

```bash
make dev
```

4. Open docs:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

## First checks

```bash
make test
make all-checks
```

## Health checks

- `GET /ping` -> `{ "status": "ok" }`
- `GET /api/v1/healthz` -> envelope with `dev_code: HEALTH_OK`
