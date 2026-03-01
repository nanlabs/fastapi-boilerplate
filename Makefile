# FastAPI Boilerplate - Development Makefile
#
# This project supports development with Dev Containers
# Requirements:
# - VS Code with Dev Containers extension, OR
# - Dev Container CLI: https://containers.dev/supporting#devcontainer-cli
#
# All commands are designed to run INSIDE the dev container environment.

.PHONY: help install install-dev clean test test-unit test-integration test-coverage lint format autofix type-check all-checks run dev init-db migration-create migration-upgrade migration-downgrade migration-history migration-current migration-stamp migration-downgrade-to migration-upgrade-to migration-show migration-merge

DIR ?= .

# Default target
help:
	@echo ""
	@echo "FastAPI Boilerplate - Development Commands"
	@echo "=========================================="
	@echo ""
	@echo "[ENV] Environment & Dependencies:"
	@echo "  install         - Install production dependencies with UV"
	@echo "  install-dev     - Install development dependencies with UV"
	@echo "  clean           - Clean build artifacts and caches"
	@echo ""
	@echo "[TEST] Testing:"
	@echo "  test            - Run all tests"
	@echo "  test-unit       - Run unit tests only"
	@echo "  test-integration- Run integration tests only"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo ""
	@echo "[QUALITY] Code Quality:"
	@echo "  lint            - Run code linting with ruff"
	@echo "  format          - Format code with ruff"
	@echo "  autofix         - Auto-fix code formatting and imports"
	@echo "  type-check      - Run type checking with mypy"
	@echo "  all-checks      - Run all code quality checks"
	@echo ""
	@echo "[DEV] Development:"
	@echo "  run             - Run FastAPI server"
	@echo "  dev             - Run FastAPI server with auto-reload"
	@echo "  init-db         - Initialize database (runs migrations + seed data)"
	@echo ""
	@echo "[DB] Database Migrations (Alembic):"
	@echo "  Note: init-db automatically runs migrations. Use these for manual control:"
	@echo "  migration-create      - Create a new migration (usage: make migration-create MESSAGE='description')"
	@echo "  migration-upgrade     - Upgrade database to head revision"
	@echo "  migration-upgrade-to  - Upgrade to specific revision (usage: make migration-upgrade-to REVISION='revision_id')"
	@echo "  migration-downgrade   - Downgrade database by one revision"
	@echo "  migration-downgrade-to - Downgrade to specific revision (usage: make migration-downgrade-to REVISION='revision_id')"
	@echo "  migration-history     - Show migration history"
	@echo "  migration-current     - Show current database revision"
	@echo "  migration-show       - Alias for migration-current"
	@echo "  migration-stamp       - Stamp database with revision (usage: make migration-stamp REVISION='revision_id')"
	@echo "  migration-merge       - Merge migration branches (usage: make migration-merge REVISIONS='rev1,rev2' MESSAGE='description')"
	@echo ""
	@echo "[ARGS] Optional directory argument:"
	@echo "  lint, format, autofix, type-check, all-checks"
	@echo "  Examples: make lint app | make all-checks tests | make all-checks DIR=app"
	@echo ""

# Install production dependencies
install:
	@echo "INFO: Installing production dependencies with UV..."
	uv sync --no-dev
	@echo "OK: Installation complete."

# Install development dependencies
install-dev:
	@echo "INFO: Installing all dependencies with UV..."
	uv sync
	@echo "OK: Installation complete."

# Clean up build artifacts and caches
clean:
	@echo "INFO: Cleaning build artifacts and caches..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .coverage.*
	rm -rf build/
	rm -rf dist/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .venv/
	@echo "OK: Cleanup complete."

# Run all tests
test:
	@echo "INFO: Running all tests..."
	uv run pytest

# Run unit tests only
test-unit:
	@echo "INFO: Running unit tests..."
	uv run pytest tests/unit -m "not integration and not slow"

# Run integration tests only
test-integration:
	@echo "INFO: Running integration tests..."
	uv run pytest tests/integration -m integration

# Run tests with coverage
test-coverage:
	@echo "INFO: Running tests with coverage..."
	uv run pytest --cov=app --cov-report=html --cov-report=term
	@echo "OK: Coverage report generated in htmlcov/"

# Run code linting
lint:
	@echo "INFO: Running code linting..."
	uv run ruff check $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))

# Format code
format:
	@echo "INFO: Formatting code..."
	uv run ruff format $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))

# Auto-fix code formatting and imports
autofix:
	@echo "INFO: Auto-fixing code..."
	uv run ruff check --fix $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	uv run ruff format $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))

# Type checking
type-check:
	@echo "INFO: Running type checking..."
	uv run mypy $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))

all-checks:
	@echo "INFO: Running all code quality checks..."
	uv run ruff check $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	uv run ruff format --check $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	uv run mypy $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	uv run bandit -c pyproject.toml -r $(or $(filter-out $@,$(MAKECMDGOALS)),$(DIR))
	@echo "OK: All code quality checks complete."

%:
	@:

# Run FastAPI server
run:
	@echo "INFO: Starting FastAPI server..."
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run FastAPI server with auto-reload
dev:
	@echo "INFO: Starting FastAPI server with auto-reload..."
	uv run python scripts/devserver.py

# Initialize database
init-db:
	@echo "INFO: Initializing database..."
	uv run python scripts/init_db.py

# Create a new migration
migration-create:
	@$(if $(MESSAGE),,echo ERROR: MESSAGE is required. Usage: make migration-create MESSAGE='description' && exit 1)
	@echo "INFO: Creating new migration: $(MESSAGE)"
	uv run alembic revision --autogenerate -m "$(MESSAGE)"

# Upgrade database to head revision
migration-upgrade:
	@echo "INFO: Upgrading database to head revision..."
	uv run alembic upgrade head

# Downgrade database by one revision
migration-downgrade:
	@echo "INFO: Downgrading database by one revision..."
	uv run alembic downgrade -1

# Show migration history
migration-history:
	@echo "INFO: Migration history:"
	uv run alembic history

# Show current database revision
migration-current:
	@echo "INFO: Current database revision:"
	uv run alembic current

# Alias for migration-current
migration-show: migration-current

# Stamp database with a specific revision
migration-stamp:
	@$(if $(REVISION),,echo ERROR: REVISION is required. Usage: make migration-stamp REVISION='revision_id' && exit 1)
	@echo "INFO: Stamping database with revision: $(REVISION)"
	uv run alembic stamp "$(REVISION)"

# Upgrade database to a specific revision
migration-upgrade-to:
	@$(if $(REVISION),,echo ERROR: REVISION is required. Usage: make migration-upgrade-to REVISION='revision_id' && exit 1)
	@echo "INFO: Upgrading database to revision: $(REVISION)"
	uv run alembic upgrade "$(REVISION)"

# Downgrade database to a specific revision
migration-downgrade-to:
	@$(if $(REVISION),,echo ERROR: REVISION is required. Usage: make migration-downgrade-to REVISION='revision_id' && exit 1)
	@echo "INFO: Downgrading database to revision: $(REVISION)"
	uv run alembic downgrade "$(REVISION)"

# Merge migration branches
migration-merge:
	@$(if $(REVISIONS),,echo ERROR: REVISIONS is required. Usage: make migration-merge REVISIONS='rev1,rev2' MESSAGE='description' && exit 1)
	@$(if $(MESSAGE),,echo ERROR: MESSAGE is required. Usage: make migration-merge REVISIONS='rev1,rev2' MESSAGE='description' && exit 1)
	@echo "INFO: Merging migration branches: $(REVISIONS)"
	uv run alembic merge -m "$(MESSAGE)" $(REVISIONS)
