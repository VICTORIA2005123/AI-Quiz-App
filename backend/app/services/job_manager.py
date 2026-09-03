import os
import hashlib
import concurrent.futures
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import ProcessingJob, DocumentMetadata, Quiz, Question, Usage
from app.models.schemas import JobState, QuizOptions, QuizSchema, QuestionSchema
from app.security.file_security import inspect_file_content_and_magic_bytes, secure_shred_file
from app.security.rate_limit import quota_manager
from app.security.audit import auditor
from app.services.parsers.document_factory import get_parser_for_extension
from app.services.normalizer import normalizer_v1
from app.services.pii_scrubber import pii_scrubber
from app.services.retrieval import retrieval_budgeter
from app.services.quiz_generator import quiz_generator_v1
from app.core.logging import logger


class JobManager:
    """
    Asynchronous Document-to-Quiz Job Manager.
    Orchestrates the background worker, tracks explicit states, supports cancellation,
    and enforces ephemeral document processing.
    """
    def __init__(self, max_workers: int = 4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.cancelled_jobs: set = set()

    def submit_job(
        self,
        user_id: str,
        filename: str,
        file_bytes: bytes,
        options: QuizOptions,
        db: Session
    ) -> str:
        # 1. Enforce Quota
        quota_manager.check_and_increment_job_quota(user_id)

        # 2. Create Initial Job Record in DB
        job = ProcessingJob(
            user_id=user_id,
            document_name=filename,
            status=JobState.QUEUED.value,
            current_step="Job queued for processing",
            progress_percentage=0
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        job_id = job.id

        auditor.log_job_lifecycle(job_id, user_id, "QUEUED")

        # 3. Dispatch to background worker
        self.executor.submit(self._execute_job_pipeline, job_id, user_id, filename, file_bytes, options)

        return job_id

    def cancel_job(self, job_id: str, user_id: str, db: Session) -> bool:
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id, ProcessingJob.user_id == user_id).first()
        if not job:
            return False

        if job.status in {JobState.COMPLETED.value, JobState.FAILED.value, JobState.CANCELLED.value}:
            return False

        self.cancelled_jobs.add(job_id)
        job.status = JobState.CANCELLED.value
        job.is_cancelled = True
        job.current_step = "Job cancelled by user"
        db.commit()

        quota_manager.release_job(user_id)
        auditor.log_job_lifecycle(job_id, user_id, "CANCELLED")
        return True

    def _update_job_state(self, db: Session, job_id: str, state: JobState, step: str, progress: int):
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if job and not job.is_cancelled:
            job.status = state.value
            job.current_step = step
            job.progress_percentage = progress
            db.commit()

    def _execute_job_pipeline(
        self,
        job_id: str,
        user_id: str,
        filename: str,
        file_bytes: bytes,
        options: QuizOptions
    ):
        db: Session = SessionLocal()
        temp_file_path = None
        try:
            # Helper for cancellation check
            def check_cancelled():
                if job_id in self.cancelled_jobs:
                    raise InterruptedError("Job was cancelled by user.")

            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
            file_hash = hashlib.sha256(file_bytes).hexdigest()

            # STEP 1: VALIDATING_FILE (10%)
            check_cancelled()
            self._update_job_state(db, job_id, JobState.VALIDATING_FILE, "Validating file security & structure", 10)
            inspect_file_content_and_magic_bytes(file_bytes, ext)

            # Record Document Metadata in DB (NO raw content stored)
            doc_meta = DocumentMetadata(
                user_id=user_id,
                file_name=filename,
                file_extension=ext,
                file_size_bytes=len(file_bytes),
                file_sha256=file_hash,
                word_count=0
            )
            db.add(doc_meta)
            db.commit()

            # STEP 2: PARSING (20%)
            check_cancelled()
            self._update_job_state(db, job_id, JobState.PARSING, "Extracting text and structure", 20)
            parser = get_parser_for_extension(ext)
            raw_text, parse_meta = parser.parse(file_bytes, filename)
            doc_meta.page_count = parse_meta.get("page_count", 1)
            doc_meta.word_count = len(raw_text.split())
            db.commit()

            # STEP 3: NORMALIZING (40%)
            check_cancelled()
            self._update_job_state(db, job_id, JobState.NORMALIZING, "Normalizing markdown hierarchy", 40)
            normalized_md = normalizer_v1.normalize_to_markdown(raw_text)

            # STEP 4: CHUNKING (50%)
            check_cancelled()
            self._update_job_state(db, job_id, JobState.CHUNKING, "Generating semantic indexed chunks with Chunk IDs", 50)
            chunks = normalizer_v1.chunk_document(normalized_md)

            # STEP 5: PII_PROCESSING (60%)
            check_cancelled()
            self._update_job_state(db, job_id, JobState.PII_PROCESSING, "Applying educational-aware PII protection", 60)
            if options.enable_pii_scrubbing:
                for c in chunks:
                    scrubbed_text, _ = pii_scrubber.scrub(c.text)
                    c.text = scrubbed_text

            # STEP 6: RETRIEVING (70%)
            check_cancelled()
            self._update_job_state(db, job_id, JobState.RETRIEVING, "Selecting key sections within token budget", 70)
            budgeted_chunks = retrieval_budgeter.select_chunks_for_quiz(chunks, options.question_count)

            # STEP 7: GENERATING (80%)
            check_cancelled()
            self._update_job_state(db, job_id, JobState.GENERATING, "Generating grounded questions via AI", 80)
            questions = quiz_generator_v1.generate_quiz(filename, budgeted_chunks, options)

            # STEP 8: VALIDATING_QUIZ & VERIFYING_EVIDENCE (90% - 95%)
            check_cancelled()
            self._update_job_state(db, job_id, JobState.VERIFYING_EVIDENCE, "Verifying citations and factual grounding", 95)

            # STEP 9: Save persistent Quiz to PostgreSQL
            quiz_title = f"Quiz: {filename}"
            quiz = Quiz(
                user_id=user_id,
                title=quiz_title,
                document_name=filename,
                difficulty=options.difficulty.value,
                bloom_level=options.bloom_level.value,
                question_count=len(questions)
            )
            db.add(quiz)
            db.commit()
            db.refresh(quiz)

            for q in questions:
                q_model = Question(
                    quiz_id=quiz.id,
                    question_type=q.type.value,
                    question_text=q.question,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    explanation=q.explanation,
                    difficulty=q.difficulty.value,
                    bloom_level=q.bloom_level.value,
                    source_chunk_id=q.source.chunk_id,
                    citation_quote=q.source.citation,
                    evidence_verified=q.source.evidence_verified,
                    confidence_score=q.source.confidence_score
                )
                db.add(q_model)
            db.commit()

            # Record Usage Token Stats
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            usage = db.query(Usage).filter(Usage.user_id == user_id, Usage.date_str == today).first()
            if not usage:
                usage = Usage(user_id=user_id, date_str=today, jobs_count=1, tokens_used=len(normalized_md) // 4)
                db.add(usage)
            else:
                usage.jobs_count += 1
                usage.tokens_used += len(normalized_md) // 4
            db.commit()

            # Complete Job
            job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
            if job and not job.is_cancelled:
                job.status = JobState.COMPLETED.value
                job.current_step = "Quiz generated and verified successfully"
                job.progress_percentage = 100
                job.result_quiz_id = quiz.id
                db.commit()

            auditor.log_job_lifecycle(job_id, user_id, "COMPLETED")

        except InterruptedError:
            logger.info(f"Job {job_id} was successfully halted due to user cancellation.")
        except Exception as e:
            logger.exception(f"Job {job_id} failed: {str(e)}")
            job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
            if job:
                job.status = JobState.FAILED.value
                job.current_step = "Job failed during processing"
                job.error_message = str(e)
                db.commit()
            auditor.log_job_lifecycle(job_id, user_id, "FAILED")
        finally:
            # Ephemeral Document Processing: Cleanup memory and shred any temp files
            if temp_file_path:
                secure_shred_file(temp_file_path)
            quota_manager.release_job(user_id)
            self.cancelled_jobs.discard(job_id)
            db.close()


job_manager = JobManager()
