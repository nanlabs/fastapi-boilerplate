# 🚀 Getting Started

> Quick start guide for FastAPI Boilerplate

## What is this?

A production-ready FastAPI boilerplate with:
- ✅ SQLite + SQLAlchemy
- ✅ Migrations with Alembic
- ✅ Complete testing
- ✅ Ruff for linting and formatting
- ✅ MyPy strict mode
- ✅ Pre-configured Dev Container
- ✅ uv package manager (ultra-fast)

## 3-Step Setup (Dev Container Required)

### 1️⃣ Choose your entry path

Use one of these options:

- **Editor (VS Code or Cursor):** open the project and click **"Reopen in Container"**
- **CLI:** run `devcontainer up --workspace-folder .`

### 2️⃣ Start inside the container

After the container is running, open the workspace in your editor and use the integrated terminal.

The container automatically runs:
```bash
make install-dev  # Installs all dependencies with uv
make init-db      # Creates and migrates the database
```

⏱️ **This takes only 1-2 minutes** thanks to uv's speed (vs 5-10 min with pip/pdm)

### 3️⃣ Done! 🎉

```bash
# See server running
make dev

# Visit API docs
# http://localhost:8000/docs
```

## Essential Commands

```bash
# Development
make dev              # Server with auto-reload
make run              # Production server

# Testing
make test             # Run tests
make test-coverage    # Tests + coverage

# Code quality
make format           # Format code
make lint             # Check linting
make type-check       # Check types
make all-checks       # Everything together

# Database
make init-db                            # Initialize DB
make migration-create MESSAGE="..."     # New migration
make migration-upgrade                  # Apply migrations

# Utilities
make clean            # Clean temporary files
make help             # See all commands
```

## Development Policy

This project is developed **only** with Dev Container.

- ✅ Valid: VS Code/Cursor + Reopen in Container
- ✅ Valid: Dev Container CLI (`devcontainer up --workspace-folder .`)
- ❌ Not supported: local/manual setup outside Dev Container

## Project Structure

```
fastapi-boilerplate/
├── app/
│   ├── api/              # 🔌 Endpoints
│   │   ├── endpoints/    # Routes
│   │   ├── schemas/      # Request/Response models
│   │   └── services/     # Business logic
│   ├── core/             # ⚙️ Configuration
│   ├── db/               # 🗄️ Database
│   │   └── models/       # SQLAlchemy models
│   └── main.py           # 🚀 Entry point
├── tests/                # 🧪 Tests
├── scripts/              # 🛠️ Scripts
├── alembic/              # 📦 Migrations
└── .devcontainer/        # 🐳 Dev Container
```

## First Development Steps

### 1. Create a Model

```python
# app/db/models/user.py
from sqlalchemy import Column, String
from app.db.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
```

### 2. Create Migration

```bash
make migration-create MESSAGE="add user table"
make migration-upgrade
```

### 3. Create Endpoint

```python
# app/api/endpoints/users.py
from fastapi import APIRouter
from app.api.schemas.user import UserResponse

router = APIRouter()

@router.get("/users", response_model=list[UserResponse])
async def get_users():
    # Your logic here
    return []
```

### 4. Register in main.py

```python
# app/main.py
from app.api.endpoints import users

app.include_router(users.router, prefix="/api/v1", tags=["users"])
```

### 5. Run and Test

```bash
make dev
# Visit http://localhost:8000/docs
```

## Configuration

Create a `.env` file (based on `.env.example`):

```bash
cp .env.example .env
```

Edit variables as needed:

```env
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=sqlite:///./app.db
ENVIRONMENT=development
DEBUG=true
```

## Testing

### Run Tests

```bash
# All tests
make test

# Only unit tests
make test-unit

# With coverage
make test-coverage
```

### Write a Test

```python
# tests/unit/test_example.py
def test_example():
    assert 1 + 1 == 2
```

## Code Quality

### Pre-commit Hooks

```bash
# Install hooks
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

### Check Quality

```bash
# Everything at once
make all-checks

# Individual
make format      # Format with Ruff
make lint        # Lint with Ruff
make type-check  # MyPy strict
```

## Deployment

### Dockerfile (basic example)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy files
COPY . .

# Install dependencies
RUN uv sync --no-dev

# Run
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔄 Change Database (SUPER EASY!)

> **Want to use PostgreSQL, MySQL or MariaDB instead of SQLite?**  
> It's extremely easy! Just 2 steps:

### Quick Switch to PostgreSQL

```bash
# 1. Change .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# 2. Add driver in pyproject.toml
dependencies = ["psycopg2-binary>=2.9.0"]

# 3. Reinstall
make install-dev

# Done! 🎉
```

**No code changes** - SQLAlchemy handles everything.

📖 **See complete guide**: For PostgreSQL, MySQL, MariaDB, Docker Compose and more, check the [Database Change Guide in Development.md](./DEVELOPMENT.md#-change-database-engine)

## Troubleshooting

### Error: "Dev Container not available"

```bash
# Install Dev Container CLI
npm install -g @devcontainers/cli

# Start container
devcontainer up --workspace-folder .
```

### Error: "Database locked"

```bash
# Close all connections and restart
make clean
make init-db
```

### Tests fail

```bash
# Clean cache and reinstall
make clean
make install-dev
make test
```

## Resources

- 📖 [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 🔧 [uv Documentation](https://docs.astral.sh/uv/)
- 🎨 [Ruff Documentation](https://docs.astral.sh/ruff/)
- 🗄️ [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- 📦 [Alembic Docs](https://alembic.sqlalchemy.org/)

## Support

- Issues: Open an issue on GitHub
- Docs: Read the complete README.md
- Refactoring: See REFACTORING.md for technical details

## Let's Code! 🚀

You're all set to start building your API. Happy coding!
