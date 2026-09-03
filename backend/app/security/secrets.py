import os
from typing import Optional
from app.core.config import settings
from app.core.logging import logger


class SecretManager:
    """
    Manages server-side credentials.
    In Development: loads from .env via settings.
    In Production: can be hooked to AWS Secrets Manager / GCP Secret Manager / Vault.
    Never exposes credentials to the client APK.
    """
    @staticmethod
    def get_gemini_api_key() -> str:
        key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if not key and settings.AI_ENV == "production":
            logger.error("CRITICAL: GEMINI_API_KEY is not configured in production environment.")
        return key

    @staticmethod
    def get_jwt_secret() -> str:
        return settings.JWT_SECRET_KEY


secret_manager = SecretManager()
