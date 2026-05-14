from fastapi import APIRouter

from app.core.config import settings


router = APIRouter()


@router.get("/health")
def check_health():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "schema": settings.DB_SCHEMA,
    }