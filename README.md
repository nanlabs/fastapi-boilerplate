# FastAPI Boilerplate

> A modern, production-ready FastAPI boilerplate with SQLite, Alembic migrations, and comprehensive tooling.

## ✨ Features

- ⚡ **FastAPI** - Modern, fast web framework for building APIs
- 🗄️ **SQLite + SQLAlchemy** - Lightweight database with powerful ORM
- 🔄 **Alembic** - Database migrations made easy
- 🧪 **Pytest** - Comprehensive testing suite
- 🎨 **Ruff** - Lightning-fast linting and formatting
- 🔍 **MyPy** - Static type checking with strict mode
- 🐳 **Dev Containers** - Consistent development environment
- 📦 **uv** - Fast Python package management

## 🚀 Quick Start

**New to this project?** → Start with the **[📖 Getting Started Guide](./docs/getting-started.md)**

### Option 1: Dev Container (Recommended)

1. Open this project in VS Code
2. Click "Reopen in Container" when prompted
3. Wait for the setup to complete (~2 minutes)
4. Run `make dev`

### Option 2: Manual Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
make install-dev

# Initialize database
make init-db

# Run server
make dev
```

Visit http://localhost:8000/docs to see the API documentation.

**Full installation guide**: [docs/getting-started.md](./docs/getting-started.md)

## 📚 Documentation

Complete documentation is available in the [`docs/`](./docs) folder:

- **[Getting Started](./docs/getting-started.md)** - Installation and first steps
- **[Development Guide](./docs/development.md)** - Creating features, testing, and best practices
- **[Architecture](./docs/architecture.md)** - Technical decisions and comparisons
- **[API Documentation](./docs/api.md)** - API endpoints and usage examples

Or visit the [Documentation Index](./docs/index.md) for a complete overview.

## 🛠️ Common Commands

```bash
make dev              # Run development server
make test             # Run tests
make test-coverage    # Run tests with coverage
make lint             # Check code quality
make format           # Format code
make all-checks       # Run all quality checks
make help             # See all available commands
```

## 📁 Project Structure

```
fastapi-boilerplate/
├── app/              # Application code
│   ├── api/          # API endpoints, schemas, services
│   ├── core/         # Configuration
│   ├── db/           # Database layer
│   │   └── models/   # SQLAlchemy models
│   └── main.py       # Application entry point
├── docs/             # Documentation
├── tests/            # Test suite
├── alembic/          # Database migrations
└── .devcontainer/    # Dev container configuration
```

## 🔗 Links

- [Swagger UI](http://localhost:8000/docs) - Interactive API documentation
- [ReDoc](http://localhost:8000/redoc) - Alternative API documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Development Guide](./docs/development.md) for details on our development process.
