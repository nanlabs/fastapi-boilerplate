"""Health check endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "thorcast-mlops-api",
    }
