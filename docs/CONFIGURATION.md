# Configuration

Configuration is environment-variable driven. Copy `.env.example` to `.env` and adjust as needed.

## Variables

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `FastAPI Boilerplate API` | Application name |
| `APP_VERSION` | `0.1.0` | API version |
| `DEBUG` | `false` | Enables debug mode and verbose logs |
| `API_PREFIX` | `/api/v1` | API base prefix |
| `HOST` | `127.0.0.1` | Bind host |
| `PORT` | `8000` | Bind port |
| `RELOAD` | `false` | Uvicorn auto-reload |
| `DATABASE_URL` | `sqlite:///./data/app.db` | Database connection string |
| `DATABASE_ECHO` | `false` | SQLAlchemy SQL logging |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Comma-separated CORS origins |

## Test-only variables

| Variable | Typical value | Effect |
|---|---|---|
| `TESTING` | `true` | Skips startup DB initialization |
| `SKIP_DB_INIT` | `true` | Explicitly skips DB initialization |

## Example for PostgreSQL

```env
DEBUG=false
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
CORS_ORIGINS=https://myapp.com,https://admin.myapp.com
HOST=0.0.0.0
```
