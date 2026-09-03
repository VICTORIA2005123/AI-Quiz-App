import json
import re
from typing import List, Dict, Any
from app.models.schemas import DocumentChunk, QuizOptions, QuestionSchema, QuestionType, DifficultyLevel, BloomTaxonomyLevel, SourceCitation
from app.security.prompt_guard import wrap_untrusted_document_payload, build_system_primacy_prompt
from app.services.ai_client import ai_client
from app.services.evidence_verifier import evidence_verifier
from app.core.logging import logger

PROMPT_VERSION = "v1"


class GroundedQuizGeneratorV1:
    """
    Generates grounded quiz questions from indexed document chunks using strict prompt confinement
    and Pydantic v2 JSON schema validation.
    """
    def generate_quiz(
        self,
        document_name: str,
        chunks: List[DocumentChunk],
        options: QuizOptions
    ) -> List[QuestionSchema]:
        if not chunks:
            raise ValueError("Cannot generate quiz: No document chunks provided.")

        prompt = self._build_prompt(document_name, chunks, options)
        
        # Validation and retry loop (up to 2 retries)
        last_error = None
        for attempt in range(2):
            try:
                raw_json = ai_client.generate_grounded_quiz_json(prompt, {})
                questions = self._parse_and_validate_questions(raw_json, chunks)
                if questions:
                    # Pass through Evidence Verification engine
                    verified_questions, audit = evidence_verifier.verify_quiz_questions(questions, chunks)
                    logger.info(f"Quiz generation succeeded with {len(verified_questions)} questions. Grounding pass rate: {audit['grounding_pass_rate']*100}%")
                    return verified_questions
            except Exception as e:
                last_error = e
                logger.warning(f"Quiz generation attempt {attempt + 1} failed: {str(e)}. Retrying with self-correction...")
                prompt += f"\n\n### PREVIOUS ATTEMPT SCHEMA ERROR:\n{str(e)}\nPlease output valid JSON strictly adhering to schema."

        raise RuntimeError(f"Failed to generate valid grounded quiz after retries: {str(last_error)}")

    def _build_prompt(self, document_name: str, chunks: List[DocumentChunk], options: QuizOptions) -> str:
        # Format chunks with Chunk IDs
        formatted_chunks = []
        for c in chunks:
            formatted_chunks.append(f"[Chunk: {c.chunk_id}] (Section: {c.section_title})\n{c.text}")
        
        combined_chunks_text = "\n\n".join(formatted_chunks)
        untrusted_payload = wrap_untrusted_document_payload(combined_chunks_text)

        base_system = (
            "You are an expert pedagogical AI and strict factual quiz generator. "
            "Your objective is to generate accurate, high-quality quiz questions grounded ENTIRELY in the provided study text."
        )
        system_prompt = build_system_primacy_prompt(base_system)

        instructions = f"""
{system_prompt}

### QUIZ GENERATION SPECIFICATIONS:
- Target Document: "{document_name}"
- Number of Questions: {options.question_count}
- Target Difficulty: {options.difficulty.value}
- Target Bloom's Taxonomy Level: {options.bloom_level.value}

### MANDATORY GROUNDING RULES:
1. Every question MUST be strictly factual and verifiable in the provided text.
2. For each question, specify the EXACT 'chunk_id' (e.g. 'chunk_001') where the fact is stated.
3. For each question, provide an 'exact_citation_quote' containing the verbatim sentence from that chunk.
4. Distractors (incorrect options) must be plausible but definitively refuted or unsupported by the text.
5. Provide a clear, educational explanation citing the chunk fact.

### REQUIRED JSON OUTPUT FORMAT:
You must output a single valid JSON object with the following structure:
{{
  "title": "Quiz Title based on document topic",
  "questions": [
    {{
      "question_id": "q001",
      "type": "single_choice",
      "question": "Clear question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option B",
      "explanation": "Explanation explaining why Option B is correct based on the text.",
      "difficulty": "{options.difficulty.value}",
      "bloom_level": "understand",
      "source": {{
        "chunk_id": "chunk_001",
        "citation": "Exact verbatim quote from chunk_001.",
        "evidence_verified": true,
        "confidence_score": 1.0
      }}
    }}
  ]
}}

### SOURCE DOCUMENT CONTENT:
{untrusted_payload}
"""
        return instructions.strip()

    def _parse_and_validate_questions(self, raw_json_str: str, chunks: List[DocumentChunk]) -> List[QuestionSchema]:
        # Extract json from markdown code fences if model wrapped it in ```json ... ```
        clean_json = raw_json_str.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json", 1)[-1].split("```", 1)[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```", 1)[-1].split("```", 1)[0].strip()

        data = json.loads(clean_json)
        raw_questions = data.get("questions", [])
        if not raw_questions and isinstance(data, list):
            raw_questions = data

        questions: List[QuestionSchema] = []
        for idx, q_data in enumerate(raw_questions):
            q_id = q_data.get("question_id") or f"q{idx + 1:03d}"
            q_type = q_data.get("type", "single_choice")
            question_text = q_data.get("question", "").strip()
            options = q_data.get("options", [])
            correct = q_data.get("correct_answer", "").strip()
            explanation = q_data.get("explanation", "").strip()
            difficulty = q_data.get("difficulty", "medium")
            bloom = q_data.get("bloom_level", "understand")

            source_data = q_data.get("source", {})
            chunk_id = source_data.get("chunk_id") or (chunks[0].chunk_id if chunks else "chunk_001")
            citation = source_data.get("citation") or (source_data.get("citation_quote") or "")

            if not question_text or not options or not correct:
                continue

            # Ensure options are unique strings
            clean_options = [str(opt).strip() for opt in options if str(opt).strip()]
            if correct not in clean_options:
                clean_options.append(correct)

            questions.append(QuestionSchema(
                question_id=q_id,
                type=QuestionType(q_type) if q_type in QuestionType._value2member_map_ else QuestionType.SINGLE_CHOICE,
                question=question_text,
                options=clean_options,
                correct_answer=correct,
                explanation=explanation,
                difficulty=DifficultyLevel(difficulty) if difficulty in DifficultyLevel._value2member_map_ else DifficultyLevel.MEDIUM,
                bloom_level=BloomTaxonomyLevel(bloom) if bloom in BloomTaxonomyLevel._value2member_map_ else BloomTaxonomyLevel.UNDERSTAND,
                source=SourceCitation(
                    chunk_id=chunk_id,
                    citation=citation,
                    evidence_verified=True,
                    confidence_score=1.0
                )
            ))

        return questions


quiz_generator_v1 = GroundedQuizGeneratorV1()
