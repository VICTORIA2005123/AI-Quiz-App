from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Quiz
from app.models.schemas import QuizSchema, QuestionSchema, SourceCitation
from app.security.auth import get_current_user_id
from app.services.exporter import quiz_exporter

router = APIRouter()


@router.get("", response_model=List[QuizSchema])
def list_user_quizzes(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).filter(Quiz.user_id == user_id).order_by(Quiz.created_at.desc()).all()
    results = []
    for quiz_model in quizzes:
        questions = [
            QuestionSchema(
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
            ) for q in quiz_model.questions
        ]
        results.append(QuizSchema(
            quiz_id=quiz_model.id,
            title=quiz_model.title,
            document_name=quiz_model.document_name,
            difficulty=quiz_model.difficulty,
            bloom_level=quiz_model.bloom_level,
            question_count=quiz_model.question_count,
            questions=questions,
            created_at=quiz_model.created_at
        ))
    return results


@router.get("/{quiz_id}", response_model=QuizSchema)
def get_quiz_detail(quiz_id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    quiz_model = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == user_id).first()
    if not quiz_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    questions = [
        QuestionSchema(
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
        ) for q in quiz_model.questions
    ]
    return QuizSchema(
        quiz_id=quiz_model.id,
        title=quiz_model.title,
        document_name=quiz_model.document_name,
        difficulty=quiz_model.difficulty,
        bloom_level=quiz_model.bloom_level,
        question_count=quiz_model.question_count,
        questions=questions,
        created_at=quiz_model.created_at
    )


@router.post("/{quiz_id}/export")
def export_quiz(quiz_id: str, export_format: str = "json", user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    quiz_schema = get_quiz_detail(quiz_id, user_id, db)
    fmt = export_format.lower()

    if fmt == "anki":
        content = quiz_exporter.export_to_anki_tsv(quiz_schema.questions)
        return Response(content=content, media_type="text/tab-separated-values", headers={"Content-Disposition": f"attachment; filename={quiz_schema.title}.txt"})
    elif fmt == "csv":
        content = quiz_exporter.export_to_csv(quiz_schema.questions)
        return Response(content=content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={quiz_schema.title}.csv"})
    elif fmt in {"md", "markdown"}:
        content = quiz_exporter.export_to_markdown_study_guide(quiz_schema)
        return Response(content=content, media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename={quiz_schema.title}.md"})
    elif fmt == "json":
        return quiz_schema
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported export format '{export_format}'")
