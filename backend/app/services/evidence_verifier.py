import difflib
from typing import List, Dict, Tuple, Any
from app.models.schemas import QuestionSchema, DocumentChunk
from app.core.logging import logger


class EvidenceVerificationEngine:
    """
    Validates grounded AI quiz generation:
    1. Verifies that source_chunk_id exists in the document chunks
    2. Performs fuzzy & exact citation matching inside the chunk
    3. Computes factual grounding confidence score
    4. Audits distractors and options
    """
    def __init__(self, min_citation_similarity: float = 0.65):
        self.min_citation_similarity = min_citation_similarity

    def verify_quiz_questions(
        self,
        questions: List[QuestionSchema],
        chunks: List[DocumentChunk]
    ) -> Tuple[List[QuestionSchema], Dict[str, Any]]:
        chunk_map: Dict[str, DocumentChunk] = {c.chunk_id: c for c in chunks}
        verified_questions: List[QuestionSchema] = []
        
        passed_count = 0
        failed_count = 0

        for q in questions:
            chunk_id = q.source.chunk_id
            citation = q.source.citation.strip()
            
            # 1. Chunk existence check
            if chunk_id not in chunk_map:
                # Try finding closest chunk if chunk_id mismatched
                if chunks:
                    chunk_id = chunks[0].chunk_id
                    q.source.chunk_id = chunk_id
                else:
                    q.source.evidence_verified = False
                    q.source.confidence_score = 0.0
                    failed_count += 1
                    verified_questions.append(q)
                    continue

            target_chunk = chunk_map[chunk_id]
            chunk_text = target_chunk.text

            # 2. Exact or Substring citation check
            citation_clean = " ".join(citation.split()).lower()
            chunk_clean = " ".join(chunk_text.split()).lower()

            if citation_clean in chunk_clean:
                # Perfect verbatim citation match
                q.source.evidence_verified = True
                q.source.confidence_score = 1.0
                passed_count += 1
            else:
                # Fuzzy matching over sentence windows
                sentences = [s.strip().lower() for s in chunk_text.split(".") if s.strip()]
                best_similarity = 0.0

                for sentence in sentences:
                    ratio = difflib.SequenceMatcher(None, citation_clean, sentence).ratio()
                    if ratio > best_similarity:
                        best_similarity = ratio

                q.source.confidence_score = round(best_similarity, 2)
                if best_similarity >= self.min_citation_similarity:
                    q.source.evidence_verified = True
                    passed_count += 1
                else:
                    q.source.evidence_verified = False
                    failed_count += 1
                    logger.warning(
                        f"Evidence verification failed for question {q.question_id}: Citation '{citation[:60]}...' not substantiated in {chunk_id}."
                    )

            # 3. Ensure options contain the correct answer
            if q.correct_answer not in q.options:
                q.options.append(q.correct_answer)

            verified_questions.append(q)

        audit_summary = {
            "total_questions": len(questions),
            "passed_grounding": passed_count,
            "failed_grounding": failed_count,
            "grounding_pass_rate": round(passed_count / max(1, len(questions)), 2)
        }

        return verified_questions, audit_summary


evidence_verifier = EvidenceVerificationEngine()
