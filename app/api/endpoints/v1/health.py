"""Health check endpoint for API v1."""

from datetime import UTC, datetime

from fastapi import APIRouter, Request

from app.api.schemas.common.responses import APIResponse, make_item_response

router = APIRouter()


@router.get(
    "/healthz",
    response_model=APIResponse[dict[str, str]],
    responses={200: {"description": "Service is healthy"}},
)
async def health_check(request: Request) -> APIResponse[dict[str, str]]:
    """Health check endpoint with standard response envelope."""
    return make_item_response(
        data={
            "status": "healthy",
            "service": "fastapi-boilerplate",
            "timestamp": datetime.now(UTC).isoformat(),
        },
        dev_code="HEALTH_OK",
        message="Service is healthy",
        request_id=getattr(request.state, "request_id", "unknown"),
    )
