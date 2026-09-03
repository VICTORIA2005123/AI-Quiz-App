from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app_name": settings.APP_NAME,
        "environment": settings.AI_ENV,
        "ai_provider": settings.AI_PROVIDER,
        "ai_model": settings.AI_MODEL,
    }


@router.get("/version")
def api_version():
    return {
        "api_version": settings.API_VERSION,
        "schema_version": "v1",
        "prompt_version": "v1",
        "normalizer_version": "v1"
    }
