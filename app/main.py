"""FastAPI application entry point."""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import (
    dataset_files,
    experiment_types,
    experiments,
    health,
    model_types,
    projects,
)
from app.core.config import settings
from app.db.init import init_database


def _configure_logging() -> None:
    """Configure application logging defaults."""
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan events."""
    # Startup: Initialize database (create tables and seed default data)
    _configure_logging()
    # Skip database initialization in test environment
    if os.getenv("TESTING") != "true" and os.getenv("SKIP_DB_INIT") != "true":
        init_database()
    yield
    # Shutdown: Cleanup if needed


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI backend for desktop app integration",
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(projects.router, prefix=f"{settings.api_prefix}/projects")
app.include_router(model_types.router, prefix=f"{settings.api_prefix}/model-types")
app.include_router(experiment_types.router, prefix=f"{settings.api_prefix}/experiment-types")
app.include_router(experiments.router, prefix=f"{settings.api_prefix}/experiments")
app.include_router(dataset_files.router, prefix=f"{settings.api_prefix}/dataset-files")


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Welcome to Thorcast MLOps API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": f"{settings.api_prefix}/healthz",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
