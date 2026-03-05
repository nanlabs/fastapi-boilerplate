"""FastAPI application entry point."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DatabaseError

from app.api.endpoints.v1 import router as v1_router
from app.api.exceptions import ConflictError, NotFoundError, SortingValidationError, ValidationError
from app.core.config import settings
from app.core.exception_handlers import (
    api_validation_handler,
    conflict_handler,
    database_error_handler,
    not_found_handler,
    request_validation_handler,
    sorting_validation_handler,
    unexpected_error_handler,
)
from app.core.logging_config import configure_logging
from app.core.middleware import RequestIDMiddleware
from app.db.init import init_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan events."""
    configure_logging(debug=settings.debug)
    if os.getenv("TESTING") != "true" and os.getenv("SKIP_DB_INIT") != "true":
        init_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI boilerplate backend",
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception handlers
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(ConflictError, conflict_handler)
app.add_exception_handler(SortingValidationError, sorting_validation_handler)
app.add_exception_handler(ValidationError, api_validation_handler)
app.add_exception_handler(RequestValidationError, request_validation_handler)
app.add_exception_handler(DatabaseError, database_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)

# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(v1_router, prefix=settings.api_prefix)


@app.get("/ping", tags=["infra"], include_in_schema=False)
async def ping() -> JSONResponse:
    """Minimal health probe for infrastructure checks."""
    return JSONResponse({"status": "ok"})


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Welcome to FastAPI Boilerplate API",
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
