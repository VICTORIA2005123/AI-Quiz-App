import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from app.db.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    jobs = relationship("ProcessingJob", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("Usage", back_populates="user", cascade="all, delete-orphan")


class DocumentMetadata(Base):
    __tablename__ = "documents_metadata"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_extension = Column(String(10), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    file_sha256 = Column(String(64), nullable=False, index=True)
    page_count = Column(Integer, default=1)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # NOTE: Raw document content and extracted text are NEVER stored here (Ephemeral Processing)


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="QUEUED", index=True)
    current_step = Column(String(100), default="Job submitted")
    progress_percentage = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    result_quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="SET NULL"), nullable=True)
    is_cancelled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="jobs")
    quiz = relationship("Quiz", foreign_keys=[result_quiz_id])


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    document_name = Column(String(255), nullable=False)
    difficulty = Column(String(50), default="medium")
    bloom_level = Column(String(50), default="mixed")
    question_count = Column(Integer, default=0)
    schema_version = Column(String(10), default="v1")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), nullable=False, index=True)
    question_type = Column(String(50), nullable=False, default="single_choice")
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of string options
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    difficulty = Column(String(50), default="medium")
    bloom_level = Column(String(50), default="understand")
    
    # Grounding & Source Citation
    source_chunk_id = Column(String(50), nullable=False)
    citation_quote = Column(Text, nullable=False)
    evidence_verified = Column(Boolean, default=True)
    confidence_score = Column(Float, default=1.0)

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quiz_id = Column(String(36), ForeignKey("quizzes.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    answers = Column(JSON, nullable=False)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    quiz = relationship("Quiz", back_populates="attempts")


class StudyProgress(Base):
    __tablename__ = "study_progress"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False, index=True)
    interval_days = Column(Integer, default=1)
    repetition_count = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)
    last_reviewed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    next_review_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class Usage(Base):
    __tablename__ = "usage"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    date_str = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    jobs_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)

    user = relationship("User", back_populates="usage_records")
