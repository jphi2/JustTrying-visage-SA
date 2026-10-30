"""Health and diagnostic endpoints."""

from fastapi import APIRouter

from app.core.config import settings
from app.services.engine_service import engine_status

router = APIRouter(tags=["System"])


@router.get("/health")
def health():

    return {
        "status": "ok",
        "application": settings.app_name,
        "version": settings.version,
    }


@router.get("/system")
def system():

    return engine_status()
