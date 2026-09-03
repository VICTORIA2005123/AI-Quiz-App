import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

# Global SlowAPI Limiter for standard endpoint throttling
limiter = Limiter(key_func=get_remote_address)


class QuotaManager:
    """
    Multi-tier rate limiter & AI cost protection guard:
    - Per IP rate limiting
    - Per Account / User rate limiting
    - Per Device session limiting
    - Daily AI job quota tracking
    - Concurrent active job tracking
    """
    def __init__(self):
        # user_id -> list of timestamps
        self.user_requests: Dict[str, list] = defaultdict(list)
        # user_id -> (count, date_str)
        self.daily_ai_usage: Dict[str, Tuple[int, str]] = defaultdict(lambda: (0, ""))
        # user_id -> active concurrent jobs count
        self.active_jobs: Dict[str, int] = defaultdict(int)

    def _get_current_date(self) -> str:
        return time.strftime("%Y-%m-%d")

    def check_and_increment_job_quota(self, user_id: str):
        today = self._get_current_date()
        count, date_str = self.daily_ai_usage[user_id]
        if date_str != today:
            count = 0

        if count >= settings.MAX_DAILY_AI_JOBS_PER_USER:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily AI generation quota exceeded ({settings.MAX_DAILY_AI_JOBS_PER_USER} jobs/day). Please upgrade or try again tomorrow."
            )

        active = self.active_jobs[user_id]
        if active >= settings.MAX_CONCURRENT_JOBS_PER_USER:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Maximum concurrent jobs ({settings.MAX_CONCURRENT_JOBS_PER_USER}) reached. Please wait for current jobs to complete."
            )

        self.daily_ai_usage[user_id] = (count + 1, today)
        self.active_jobs[user_id] += 1

    def release_job(self, user_id: str):
        if self.active_jobs[user_id] > 0:
            self.active_jobs[user_id] -= 1

    def get_user_quota_status(self, user_id: str) -> Dict[str, int]:
        today = self._get_current_date()
        count, date_str = self.daily_ai_usage[user_id]
        if date_str != today:
            count = 0
        return {
            "daily_used": count,
            "daily_limit": settings.MAX_DAILY_AI_JOBS_PER_USER,
            "daily_remaining": max(0, settings.MAX_DAILY_AI_JOBS_PER_USER - count),
            "active_concurrent": self.active_jobs[user_id],
            "max_concurrent": settings.MAX_CONCURRENT_JOBS_PER_USER
        }


quota_manager = QuotaManager()
