import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App & Environment
    APP_NAME: str = "Secure AI Quiz Backend"
    API_VERSION: str = "v1"
    DEBUG: bool = False
    AI_ENV: Literal["development", "testing", "production"] = "development"

    # Security & Authentication
    JWT_SECRET_KEY: str = "change-this-super-secret-key-for-production-min-32-chars!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI Provider
    AI_PROVIDER: str = "gemini"
    AI_MODEL: str = "gemini-2.0-flash"
    AI_MOCK_MODEL: str = "local-mock-v1"
    GEMINI_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    # Strict Resource & Processing Limits
    MAX_FILE_SIZE_BYTES: int = 26214400  # 25 MB
    MAX_DOCUMENT_PAGES: int = 100
    MAX_EXTRACTED_CHARS: int = 250000
    MAX_CHUNKS_PER_DOC: int = 50
    MAX_OCR_PAGES: int = 10
    MAX_AI_TOKENS_PER_JOB: int = 16000
    MAX_QUESTIONS_PER_JOB: int = 25
    MAX_JOB_PROCESSING_TIMEOUT_SECONDS: int = 120
    MAX_CONCURRENT_JOBS_PER_USER: int = 2
    MAX_DAILY_AI_JOBS_PER_USER: int = 10

    # Ephemeral Storage Cleanup
    EPHEMERAL_FILE_TTL_SECONDS: int = 3600

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
