# Database Guide

## Default: SQLite

No extra configuration is needed. The database file is created at `data/app.db` on first run.

```bash
make dev
```

## Switching to PostgreSQL

Set only `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
```

Install driver:

```bash
uv add psycopg2-binary
```

## Dev Container + PostgreSQL

Add a compose file in `.devcontainer/docker-compose.yml` with `app` and `db` services, then point `devcontainer.json` to it and set `DATABASE_URL=postgresql://postgres:postgres@db:5432/boilerplate`.

Rebuild container after changes.

## Migrations

```bash
make migration-create MESSAGE="add users table"
make migration-upgrade
make migration-current
make migration-history
make migration-downgrade
```

## Troubleshooting

- `sqlite3.OperationalError: unable to open database file`: run `make init-db`.
- PostgreSQL connection errors: verify DB service and `DATABASE_URL`.
- Alembic multiple heads: create a merge migration.
