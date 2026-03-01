"""API v1 router that aggregates all v1 endpoints."""

from fastapi import APIRouter

from app.api.endpoints.v1 import health, projects

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(projects.router, prefix="/projects", tags=["projects"])
