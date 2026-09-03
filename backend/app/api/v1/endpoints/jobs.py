from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import ProcessingJob, Quiz
from app.models.schemas import JobStatusResponse, JobState, QuizOptions, DifficultyLevel, BloomTaxonomyLevel, QuizSchema, QuestionSchema, SourceCitation
from app.security.auth import get_current_user_id
from app.security.file_security import validate_file_metadata
from app.services.job_manager import job_manager

router = APIRouter()


@router.post("", response_model=JobStatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_document_for_quiz(
    file: UploadFile = File(...),
    question_count: int = Form(default=5),
    difficulty: str = Form(default="medium"),
    bloom_level: str = Form(default="mixed"),
    enable_pii_scrubbing: bool = Form(default=True),
    strict_grounding: bool = Form(default=True),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    filename, ext = validate_file_metadata(file)
    content = await file.read()

    options = QuizOptions(
        question_count=question_count,
        difficulty=DifficultyLevel(difficulty.lower()) if difficulty.lower() in DifficultyLevel._value2member_map_ else DifficultyLevel.MEDIUM,
        bloom_level=BloomTaxonomyLevel(bloom_level.lower()) if bloom_level.lower() in BloomTaxonomyLevel._value2member_map_ else BloomTaxonomyLevel.MIXED,
        enable_pii_scrubbing=enable_pii_scrubbing,
        strict_grounding=strict_grounding
    )

    job_id = job_manager.submit_job(
        user_id=user_id,
        filename=filename,
        file_bytes=content,
        options=options,
        db=db
    )

    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    return JobStatusResponse(
        job_id=job.id,
        status=JobState(job.status),
        current_step=job.current_step,
        progress_percentage=job.progress_percentage,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id, ProcessingJob.user_id == user_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    quiz_schema = None
    if job.status == JobState.COMPLETED.value and job.result_quiz_id:
        quiz_model = db.query(Quiz).filter(Quiz.id == job.result_quiz_id).first()
        if quiz_model:
            questions = []
            for q in quiz_model.questions:
                questions.append(QuestionSchema(
                    question_id=q.id,
                    type=q.question_type,
                    question=q.question_text,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    explanation=q.explanation,
                    difficulty=q.difficulty,
                    bloom_level=q.bloom_level,
                    source=SourceCitation(
                        chunk_id=q.source_chunk_id,
                        citation=q.citation_quote,
                        evidence_verified=q.evidence_verified,
                        confidence_score=q.confidence_score
                    )
                ))
            quiz_schema = QuizSchema(
                quiz_id=quiz_model.id,
                title=quiz_model.title,
                document_name=quiz_model.document_name,
                difficulty=quiz_model.difficulty,
                bloom_level=quiz_model.bloom_level,
                question_count=quiz_model.question_count,
                questions=questions,
                created_at=quiz_model.created_at
            )

    return JobStatusResponse(
        job_id=job.id,
        status=JobState(job.status),
        current_step=job.current_step,
        progress_percentage=job.progress_percentage,
        error_message=job.error_message,
        quiz=quiz_schema,
        created_at=job.created_at,
        updated_at=job.updated_at
    )


@router.post("/{job_id}/cancel")
def cancel_running_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    cancelled = job_manager.cancel_job(job_id, user_id, db)
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be cancelled (either not found, or already completed/failed/cancelled)."
        )
    return {"message": "Job successfully cancelled", "job_id": job_id}
