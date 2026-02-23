# 💻 Development Guide

## Table of Contents

- [Project Structure](#project-structure)
- [Environment Setup](#environment-setup)
- [Creating New Features](#creating-new-features)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Database](#database)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Project Structure

```
fastapi-boilerplate/
├── app/
│   ├── api/                    # API Layer
│   │   ├── endpoints/          # Route definitions
│   │   ├── schemas/            # Request/Response models (Pydantic)
│   │   └── services/           # Business logic
│   ├── core/                   # Core configuration
│   │   └── config.py           # Environment variables and settings
│   ├── db/                     # Database layer
│   │   ├── models/             # SQLAlchemy models
│   │   ├── session.py          # DB session
│   │   ├── init.py             # Initialization
│   │   └── seed_data.py        # Initial data
│   └── main.py                 # Application entry point
├── alembic/                    # Database migrations
│   └── versions/               # Migration files
├── config/                     # Configuration files
│   └── seed_data.yaml          # Seed data in YAML
├── scripts/                    # Utility scripts
│   ├── init_db.py              # Initialize database
│   └── devserver.py            # Development server
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── conftest.py             # Pytest configuration
│   └── helpers.py              # Testing utilities
└── .devcontainer/              # Dev Container configuration
```

## Environment Setup

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Available variables:

```env
# API Configuration
API_HOST=0.0.0.0              # Server host
API_PORT=8000                  # Server port
API_TITLE=FastAPI Boilerplate  # Title in documentation
API_VERSION=0.1.0              # API version

# Database
DATABASE_URL=sqlite:///./app.db  # DB connection URL

# Environment
ENVIRONMENT=development        # development, staging, production
DEBUG=true                     # Debug mode

# Logging
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR, CRITICAL

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Available Commands

See all available commands:

```bash
make help
```

Main commands:

```bash
# Installation
make install           # Production dependencies only
make install-dev       # All dependencies (includes dev)

# Development
make dev               # Server with auto-reload
make run               # Production server

# Testing
make test              # Run all tests
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-coverage     # Tests with coverage report

# Code quality
make lint              # Check linting (Ruff)
make format            # Format code (Ruff)
make autofix           # Auto-fix + format
make type-check        # Type checking (MyPy)
make all-checks        # Run all checks

# Database
make init-db                            # Initialize DB
make migration-create MESSAGE="..."     # Create new migration
make migration-upgrade                  # Apply migrations
make migration-downgrade                # Revert last migration
make migration-history                  # View history
make migration-current                  # View current migration

# Cleanup
make clean             # Clean temporary files and cache
```

## Creating New Features

### 1. Create a Database Model

```python
# app/db/models/user.py
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.db.models.base import Base

class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    # posts = relationship("Post", back_populates="author")
```

### 2. Register the Model

```python
# app/db/models/__init__.py
from app.db.models.base import Base
from app.db.models.user import User  # Add this line

__all__ = ["Base", "User"]
```

### 3. Create Migration

```bash
make migration-create MESSAGE="add user table"
```

This generates a file in `alembic/versions/`. Review it and apply:

```bash
make migration-upgrade
```

### 4. Create Pydantic Schemas

```python
# app/api/schemas/user.py
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)

class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None

class UserResponse(UserBase):
    """Schema for user responses."""
    id: str
    is_active: bool
    
    model_config = {"from_attributes": True}

class UserListResponse(BaseModel):
    """Schema for listing users."""
    users: list[UserResponse]
    total: int
```

### 5. Create Service (Business Logic)

```python
# app/api/services/user_service.py
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.api.schemas.user import UserCreate, UserUpdate

class UserService:
    """Service for user operations."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user(db: Session, user_id: str) -> User | None:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users."""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> User | None:
        """Update user."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """Delete user."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
```

### 6. Create Endpoints

```python
# app/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.schemas.user import UserCreate, UserResponse, UserListResponse, UserUpdate
from app.api.services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Create a new user."""
    try:
        user = UserService.create_user(db, user_data)
        return UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user: {str(e)}"
        )

@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> UserListResponse:
    """List all users."""
    users = UserService.list_users(db, skip=skip, limit=limit)
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=len(users)
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Get user by ID."""
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Update user."""
    user = UserService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
) -> None:
    """Delete user."""
    deleted = UserService.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
```

### 7. Register Router in main.py

```python
# app/main.py
from app.api.endpoints import users

# ... existing code ...

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["users"]
)
```

### 8. Test in Swagger

1. Run the server: `make dev`
2. Visit: http://localhost:8000/docs
3. Test the created endpoints

## Testing

### Test Structure

```
tests/
├── unit/              # Unit tests (no DB)
│   ├── api/
│   ├── db/
│   └── services/
├── integration/       # Integration tests (with DB)
│   └── api/
├── conftest.py        # Shared fixtures
└── helpers.py         # Utilities
```

### Writing Unit Tests

```python
# tests/unit/services/test_user_service.py
import pytest
from unittest.mock import Mock
from app.api.services.user_service import UserService
from app.api.schemas.user import UserCreate

def test_create_user():
    """Test user creation."""
    # Arrange
    db_mock = Mock()
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    
    # Act
    user = UserService.create_user(db_mock, user_data)
    
    # Assert
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()
```

### Integration Tests

```python
# tests/integration/api/test_users.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user_endpoint():
    """Test user creation endpoint."""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data
```

### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration only
make test-integration

# With coverage
make test-coverage
```

## Code Quality

### Ruff (Linting and Formatting)

Ruff replaces black, isort, flake8, and pylint.

```bash
# Check issues
make lint

# Format code
make format

# Auto-fix and format
make autofix
```

### MyPy (Type Checking)

The project uses MyPy in strict mode.

```bash
make type-check
```

### Pre-commit Hooks

Install hooks:

```bash
uv run pre-commit install
```

Hooks will run automatically before each commit:
- Trailing whitespace
- End of file fixer
- YAML/JSON/TOML checks
- Ruff linting and formatting
- MyPy
- Bandit (security)

Run manually:

```bash
uv run pre-commit run --all-files
```

### Run All Checks

```bash
make all-checks
```

## Database

### Local SQLite

Uses SQLite by default: `sqlite:///./app.db`

### Migrations with Alembic

```bash
# Create new migration
make migration-create MESSAGE="add user email field"

# Apply migrations
make migration-upgrade

# Revert last migration
make migration-downgrade

# View history
make migration-history

# View current migration
make migration-current
```

### 🔄 Change Database Engine

> **It's EXTREMELY EASY!** 🚀 SQLAlchemy abstracts the engine, you only need to change the connection URL.

#### Why It's So Easy

✅ **No code changes** - SQLAlchemy models work with any engine  
✅ **No query rewriting** - The ORM handles the differences  
✅ **Migrations work the same** - Alembic supports all engines  
✅ **Only 2 steps** - Change URL + add driver

#### 📊 Supported Engines

| Engine | Ease | Use Case | Production |
|--------|------|----------|-----------|
| **SQLite** | ⭐⭐⭐⭐⭐ | Development, prototypes | ❌ |
| **PostgreSQL** | ⭐⭐⭐⭐⭐ | Serious applications | ✅ Recommended |
| **MySQL** | ⭐⭐⭐⭐ | Legacy, WordPress ecosystem | ✅ |
| **MariaDB** | ⭐⭐⭐⭐ | MySQL compatible, more features | ✅ |

---

### 🐘 Switch to PostgreSQL (Recommended)

**Step 1**: Change `.env`

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Or with async (better performance):
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

**Step 2**: Add driver in `pyproject.toml`

```toml
dependencies = [
    # ... existing ...
    "psycopg2-binary>=2.9.0",    # For sync
    # Or for async (recommended):
    # "asyncpg>=0.29.0",
]
```

**Step 3**: Reinstall and migrate

```bash
make install-dev
make migration-upgrade
```

**Done!** 🎉 Your app now uses PostgreSQL.

#### PostgreSQL with Docker

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

```bash
docker-compose up -d
# Then change .env to: DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/mydb
```

---

### 🐬 Switch to MySQL/MariaDB

**Step 1**: Change `.env`

```env
# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname

# MariaDB (same syntax)
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
```

**Step 2**: Add driver in `pyproject.toml`

```toml
dependencies = [
    # ... existing ...
    "pymysql>=1.1.0",
    "cryptography>=41.0.0",  # Required by pymysql
]
```

**Step 3**: Reinstall and migrate

```bash
make install-dev
make migration-upgrade
```

#### MySQL with Docker

```yaml
# docker-compose.yml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mydb
      MYSQL_USER: myuser
      MYSQL_PASSWORD: mypassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

#### MariaDB with Docker

```yaml
# docker-compose.yml
version: '3.8'
services:
  mariadb:
    image: mariadb:11
    environment:
      MARIADB_ROOT_PASSWORD: rootpassword
      MARIADB_DATABASE: mydb
      MARIADB_USER: myuser
      MARIADB_PASSWORD: mypassword
    ports:
      - "3306:3306"
    volumes:
      - mariadb_data:/var/lib/mysql

volumes:
  mariadb_data:
```

---

### ⚙️ Connection Pool Configuration

For production, it's important to configure the pool correctly:

```python
# app/db/session.py
from sqlalchemy import create_engine

engine = create_engine(
    settings.resolved_database_url,
    pool_size=20,              # Number of connections in pool
    max_overflow=0,            # Extra connections allowed
    pool_timeout=30,           # Timeout to get connection
    pool_recycle=3600,         # Recycle connections every hour
    pool_pre_ping=True,        # Check connection before using
)
```

**Recommendations by engine:**

```python
# PostgreSQL (better connection handling)
pool_size=20
max_overflow=10

# MySQL/MariaDB (more conservative)
pool_size=10
max_overflow=5
pool_recycle=3600  # Important for MySQL

# SQLite (no pool needed)
pool_size=0
```

---

### 🔐 Complete Connection URLs

#### PostgreSQL

```env
# Basic
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# With SSL
DATABASE_URL=postgresql://user:password@host:5432/db?sslmode=require

# With specific schema
DATABASE_URL=postgresql://user:password@host:5432/db?options=-c%20search_path=myschema

# Async (better performance)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db
```

#### MySQL/MariaDB

```env
# Basic
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname

# With charset
DATABASE_URL=mysql+pymysql://user:password@host:3306/db?charset=utf8mb4

# With SSL
DATABASE_URL=mysql+pymysql://user:password@host:3306/db?ssl_ca=/path/to/ca.pem
```

#### SQLite

```env
# Relative to project
DATABASE_URL=sqlite:///./app.db

# Absolute
DATABASE_URL=sqlite:////absolute/path/to/app.db

# In memory (testing)
DATABASE_URL=sqlite:///:memory:
```

---

### 🎯 Complete Example: Migrate to PostgreSQL

**Scenario**: You have an app with SQLite in development and want to move it to PostgreSQL for production.

**1. Start PostgreSQL locally**

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=mypass \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  postgres:16
```

**2. Update `.env`**

```bash
# Before
DATABASE_URL=sqlite:///./app.db

# After
DATABASE_URL=postgresql://postgres:mypass@localhost:5432/mydb
```

**3. Add driver**

```bash
# Edit pyproject.toml
dependencies = [
    # ...
    "psycopg2-binary>=2.9.0",
]
```

**4. Reinstall**

```bash
make install-dev
```

**5. Apply migrations**

```bash
make migration-upgrade
```

**6. Initialize data (optional)**

```bash
make init-db
```

**7. Done!**

```bash
make dev
# Your app now runs with PostgreSQL 🎉
```

**Total code changes**: **0 lines** ✨

---

### 💡 Tips and Best Practices

#### 1. Use Different Environment Variables

```env
# .env.development
DATABASE_URL=sqlite:///./app.db

# .env.production
DATABASE_URL=postgresql://user:pass@prod-host/db
```

#### 2. Backup Before Migrating

```bash
# SQLite
cp app.db app.db.backup

# PostgreSQL
pg_dump -U user dbname > backup.sql

# MySQL
mysqldump -u user -p dbname > backup.sql
```

#### 3. Test in Development First

```bash
# 1. Create test DB
docker run -d -e POSTGRES_PASSWORD=test -p 5433:5432 postgres:16

# 2. Use different port
DATABASE_URL=postgresql://postgres:test@localhost:5433/postgres

# 3. Test that everything works
make test
```

#### 4. Consider Async for Performance

```python
# For high-load apps, use async drivers:
# PostgreSQL: asyncpg
# MySQL: aiomysql
```

---

### 🐛 Troubleshooting

#### Error: "no such driver"

```bash
# You forgot to install the driver
make install-dev
```

#### Error: "connection refused"

```bash
# Verify DB is running
docker ps
# Or
psql -h localhost -U user -d dbname  # PostgreSQL
mysql -h localhost -u user -p dbname # MySQL
```

#### Error: "migrations failed"

```bash
# Clean and restart
make migration-downgrade  # Or delete the DB
make migration-upgrade
```

#### SQLite works but PostgreSQL doesn't

```bash
# Check differences in data types
# SQLite is more permissive, PostgreSQL stricter
# Make sure your models have correct types
```

---

### 📈 Performance Comparison

| Operation | SQLite | PostgreSQL | MySQL |
|-----------|--------|-----------|--------|
| Simple reads | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Concurrent writes | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Complex queries | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Scalability | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Setup ease | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

**Recommendation**:
- Development: SQLite (already configured)
- Production: PostgreSQL (best overall choice)
- Legacy/specific: MySQL/MariaDB

## Deployment

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy files
COPY pyproject.toml .
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .
COPY scripts/ scripts/

# Install production dependencies
RUN uv sync --no-dev

# Run migrations and start server
CMD uv run alembic upgrade head && \
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Production Environment Variables

```env
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://...
LOG_LEVEL=WARNING
```

## Troubleshooting

### Error: "Dev Container not available"

```bash
# Install Dev Container CLI
npm install -g @devcontainers/cli

# Start container
devcontainer up --workspace-folder .
```

### Error: "Database is locked"

```bash
# Close all connections
make clean
rm -f app.db
make init-db
```

### Tests fail

```bash
# Clean cache
make clean
make install-dev
make test
```

### Import errors

Verify that `PYTHONPATH` includes the root directory:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

In Dev Container this is already configured.

### Slow tests

Mark slow tests:

```python
@pytest.mark.slow
def test_slow_operation():
    ...
```

Exclude them:

```bash
pytest -m "not slow"
```

## Best Practices

### 1. Separation of Concerns

- **Models**: DB definition only
- **Schemas**: Validation and serialization
- **Services**: Business logic
- **Endpoints**: Routing and HTTP validation only

### 2. Type Hints

Use type hints throughout the code:

```python
def get_user(user_id: str) -> User | None:
    ...
```

### 3. Dependency Injection

Use FastAPI dependencies:

```python
async def endpoint(db: Session = Depends(get_db)):
    ...
```

### 4. Error Handling

```python
try:
    result = service.operation()
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### 5. Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Operation successful")
logger.error("Operation failed", exc_info=True)
```

## Resources

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy 2.0 Style](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [Pytest Documentation](https://docs.pytest.org/)
