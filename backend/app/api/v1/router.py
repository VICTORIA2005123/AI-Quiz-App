from fastapi import APIRouter
from app.api.v1.endpoints import auth, jobs, quizzes, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Quotas"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Document Ingestion & Async Jobs"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["Quizzes & Exports"])
