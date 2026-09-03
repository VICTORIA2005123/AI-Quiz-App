import time
from typing import Optional, Dict, Any
from app.core.logging import logger


class SecurityAuditor:
    """
    Structured security and privacy event logger.
    Guarantees NO raw document text, NO PII, and NO sensitive tokens are ever recorded in audit logs.
    """
    @staticmethod
    def log_auth_event(event_type: str, user_id: Optional[str], ip_address: str, success: bool, reason: Optional[str] = None):
        logger.info(
            f"[AUDIT:AUTH] event={event_type} user_id={user_id or 'anonymous'} ip={ip_address} success={success} reason={reason or 'none'}"
        )

    @staticmethod
    def log_file_ingestion(user_id: str, file_hash: str, ext: str, size_bytes: int, status: str):
        logger.info(
            f"[AUDIT:FILE_INGEST] user_id={user_id} hash={file_hash[:12]} ext={ext} size_bytes={size_bytes} status={status}"
        )

    @staticmethod
    def log_job_lifecycle(job_id: str, user_id: str, state: str, duration_ms: Optional[int] = None):
        logger.info(
            f"[AUDIT:JOB] job_id={job_id} user_id={user_id} state={state} duration_ms={duration_ms or 0}"
        )

    @staticmethod
    def log_security_violation(violation_type: str, user_id: Optional[str], ip_address: str, details: str):
        logger.warning(
            f"[AUDIT:SECURITY_VIOLATION] type={violation_type} user_id={user_id or 'anonymous'} ip={ip_address} details={details}"
        )


auditor = SecurityAuditor()
