import re
import html
from typing import Optional
from fastapi import HTTPException, status


def sanitize_text(text: Optional[str], max_length: int = 1000) -> str:
    if not text:
        return ""
    # Strip dangerous HTML/script tags and normalize whitespace
    cleaned = html.escape(text.strip())
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned


def validate_difficulty(difficulty: str) -> str:
    allowed = {"easy", "medium", "hard", "adaptive"}
    if difficulty.lower() not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid difficulty '{difficulty}'. Allowed: {', '.join(allowed)}"
        )
    return difficulty.lower()


def validate_bloom_level(level: str) -> str:
    allowed = {"remember", "understand", "apply", "analyze", "evaluate", "create", "mixed"}
    if level.lower() not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid Bloom's taxonomy level '{level}'. Allowed: {', '.join(allowed)}"
        )
    return level.lower()


def validate_question_count(count: int, max_count: int = 25) -> int:
    if count < 1 or count > max_count:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Question count must be between 1 and {max_count}."
        )
    return count
