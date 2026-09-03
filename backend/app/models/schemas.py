from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class JobState(str, Enum):
    QUEUED = "QUEUED"
    VALIDATING_FILE = "VALIDATING_FILE"
    PARSING = "PARSING"
    OCR_PROCESSING = "OCR_PROCESSING"
    NORMALIZING = "NORMALIZING"
    CHUNKING = "CHUNKING"
    PII_PROCESSING = "PII_PROCESSING"
    RETRIEVING = "RETRIEVING"
    GENERATING = "GENERATING"
    VALIDATING_QUIZ = "VALIDATING_QUIZ"
    VERIFYING_EVIDENCE = "VERIFYING_EVIDENCE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    TRUE_FALSE = "true_false"
    MULTI_SELECT = "multi_select"
    FLASHCARD = "flashcard"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ADAPTIVE = "adaptive"


class BloomTaxonomyLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"
    MIXED = "mixed"


# Document Chunk Model
class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier, e.g. chunk_001")
    section_title: str = Field(default="General", description="Section header or title")
    text: str = Field(..., description="Normalized chunk text")
    start_char: int = Field(default=0)
    end_char: int = Field(default=0)
    word_count: int = Field(default=0)


# Source Citation
class SourceCitation(BaseModel):
    document_id: Optional[str] = Field(default=None, description="Document identifier")
    chunk_id: str = Field(..., description="Source chunk ID, e.g. chunk_014")
    citation: str = Field(..., description="Exact verbatim quotation from the designated chunk")
    evidence_verified: bool = Field(default=True, description="Grounding verification result")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Factual grounding confidence")


# Single Question Schema
class QuestionSchema(BaseModel):
    question_id: str = Field(..., description="Question identifier, e.g. q001")
    type: QuestionType = Field(default=QuestionType.SINGLE_CHOICE)
    question: str = Field(..., description="Question text")
    options: List[str] = Field(..., description="List of possible answer options")
    correct_answer: str = Field(..., description="Exact string of the correct answer")
    explanation: str = Field(..., description="Detailed explanation grounded in the document")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    bloom_level: BloomTaxonomyLevel = Field(default=BloomTaxonomyLevel.UNDERSTAND)
    source: SourceCitation = Field(..., description="Source chunk citation and evidence proof")


# Quiz Schema
class QuizSchema(BaseModel):
    quiz_id: str
    title: str
    document_name: str
    difficulty: str
    bloom_level: str
    question_count: int
    questions: List[QuestionSchema]
    created_at: datetime


# Quiz Generation Parameters
class QuizOptions(BaseModel):
    question_count: int = Field(default=5, ge=1, le=25)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    bloom_level: BloomTaxonomyLevel = Field(default=BloomTaxonomyLevel.MIXED)
    enable_pii_scrubbing: bool = Field(default=True)
    strict_grounding: bool = Field(default=True)


# Job Status Response
class JobStatusResponse(BaseModel):
    job_id: str
    status: JobState
    current_step: str
    progress_percentage: int
    error_message: Optional[str] = None
    quiz: Optional[QuizSchema] = None
    created_at: datetime
    updated_at: datetime


# User Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class QuotaResponse(BaseModel):
    daily_used: int
    daily_limit: int
    daily_remaining: int
    active_concurrent: int
    max_concurrent: int
