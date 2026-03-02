# Getting Started

## Goal 🎯

Reach a successful local run in 10-15 minutes with tests and checks passing.

## Prerequisites

- Docker running locally.
- Editor with Dev Container support (Cursor or VS Code), or Dev Container CLI.
- No host Python setup required (everything runs in container).

Minimum host setup:

1. Install `git`.
2. Install Docker + Docker Compose.
3. Install Dev Container CLI.
4. Optional: install `pre-commit` for fast local hooks.

## Host vs Container contract

- Run `git` commands on host if you want (status/add/commit/push).
- Run project/runtime commands in Dev Container (`make test`, `make all-checks`, `make dev`, migrations).
- If you are on host terminal, use:

```bash
devcontainer exec --workspace-folder . make <target>
```

## Step 1: Open in Dev Container 🐳

Use one option:

```bash
# CLI
devcontainer up --workspace-folder .
```

Or open the repo in your editor and choose **Reopen in Container**.

## Step 2: Install and initialize

Inside the container:

```bash
make install-dev
make init-db
```

Alternative one-shot setup:

```bash
make bootstrap
```

## Step 3: Run the API

```bash
make dev
```

API endpoints:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Step 4: Validate your setup ✅

From another terminal in the same container:

```bash
curl -s http://localhost:8000/ping
curl -s http://localhost:8000/api/v1/healthz
make test
make all-checks
make doctor
```

Expected:

- `/ping` returns `{ "status": "ok" }`
- `/api/v1/healthz` returns envelope with `dev_code: HEALTH_OK`
- tests and checks complete successfully

## Cross-platform smoke checklist

Run this after cloning on Linux, macOS, or Windows:

1. `devcontainer up --workspace-folder .`
2. `devcontainer exec --workspace-folder . make doctor`
3. `devcontainer exec --workspace-folder . make test-unit`
4. `git status` should not show unrelated line-ending changes.

## Common first-run issues

- Port busy on `8000`: stop local process using that port or remap forwarded port.
- Container dependency issue: rebuild container and rerun `make install-dev`.
- DB lock or file errors on SQLite: run `make init-db` again.
- Git auth fails in container:
  - HTTPS: ensure host credential helper is configured.
  - SSH: ensure host SSH agent is running and key is loaded (`ssh-add`).
- Massive modified-file diffs after clone on Windows/macOS:
  - check Git line ending settings and pull latest `.gitattributes`.
  - re-run checkout if needed.

See `TIPS_AND_TRICKS.md` for troubleshooting shortcuts.

## Related docs

- `DEVELOPMENT.md` for the recommended first feature workflow.
- `DEVELOPMENT.md` for resource implementation conventions.
- `DATABASE.md` for migrations and PostgreSQL setup.
