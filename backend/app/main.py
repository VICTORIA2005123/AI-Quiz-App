from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base
from app.db.session import engine
from app.api.v1.router import api_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Enterprise-grade, privacy-first Document-to-Quiz API with Grounded AI and Ephemeral Processing.",
    docs_url=f"/api/{settings.API_VERSION}/docs",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response


# Rate Limit Exception Handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please throttle your requests."}
    )


# Mount API Router
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")


@app.get("/")
def root():
    return {
        "message": "Secure AI Quiz API is running",
        "docs": f"/api/{settings.API_VERSION}/docs",
        "version": settings.API_VERSION
    }
