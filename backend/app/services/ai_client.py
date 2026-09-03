import json
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging import logger
from app.security.secrets import secret_manager


class AIClient:
    """
    Generic AI Provider Client:
    - In Development: Uses configured Gemini model or Mock if API key absent
    - In Testing: Uses deterministic Mock model
    - In Production: Uses configured production Gemini model. On failure, raises explicit exception.
    """
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.model_name = settings.AI_MODEL
        self.env = settings.AI_ENV

    def generate_grounded_quiz_json(self, prompt: str, schema_dict: Dict[str, Any]) -> str:
        if self.env == "testing":
            return self._generate_mock_quiz_json(prompt)

        api_key = secret_manager.get_gemini_api_key()
        if not api_key:
            if self.env == "production":
                raise RuntimeError("Production AI generation failed: GEMINI_API_KEY is not configured on server.")
            logger.warning("No GEMINI_API_KEY detected in development environment; generating grounded mock quiz.")
            return self._generate_mock_quiz_json(prompt)

        try:
            # First try google.genai SDK
            import google.genai as genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            return response.text
        except Exception as e:
            logger.warning(f"google.genai call encountered: {e}. Attempting google.generativeai fallback...")
            try:
                import google.generativeai as legacy_genai
                legacy_genai.configure(api_key=api_key)
                model = legacy_genai.GenerativeModel(
                    self.model_name,
                    generation_config={"response_mime_type": "application/json"}
                )
                response = model.generate_content(prompt)
                return response.text
            except Exception as e2:
                if self.env == "production":
                    raise RuntimeError(f"Production Gemini AI generation failed: {str(e2)}")
                logger.error(f"Gemini API error in development: {str(e2)}. Falling back to local mock generator.")
                return self._generate_mock_quiz_json(prompt)

    def _generate_mock_quiz_json(self, prompt: str) -> str:
        """
        Deterministic mock generator for testing & offline development.
        Parses chunk text from prompt to ensure generated questions are authentically grounded.
        """
        # Extract chunk ID from prompt if available
        import re
        chunk_match = re.search(r"\[Chunk:\s*(chunk_\d+)\]\s*(.*?)(?=\[Chunk:|$)", prompt, re.DOTALL)
        chunk_id = chunk_match.group(1) if chunk_match else "chunk_001"
        chunk_text = chunk_match.group(2).strip() if chunk_match else "General document content."

        first_sentence = chunk_text.split(".")[0].strip() if "." in chunk_text else "Key concept discussed in document"
        if len(first_sentence) > 120:
            first_sentence = first_sentence[:120]

        mock_data = {
            "title": "Grounded Document Quiz",
            "questions": [
                {
                    "question_id": "q001",
                    "type": "single_choice",
                    "question": f"According to the source text, which statement is accurately stated regarding: '{first_sentence[:50]}...'?",
                    "options": [
                        f"{first_sentence}.",
                        "It contradicts foundational principles.",
                        "It was proven completely irrelevant.",
                        "It operates independently of any parameters."
                    ],
                    "correct_answer": f"{first_sentence}.",
                    "explanation": f"This is explicitly stated in {chunk_id}.",
                    "difficulty": "medium",
                    "bloom_level": "understand",
                    "source": {
                        "chunk_id": chunk_id,
                        "citation": first_sentence,
                        "evidence_verified": True,
                        "confidence_score": 1.0
                    }
                },
                {
                    "question_id": "q002",
                    "type": "true_false",
                    "question": f"True or False: The document confirms that '{first_sentence[:60]}...'",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": f"Directly confirmed in {chunk_id}: '{first_sentence}'.",
                    "difficulty": "easy",
                    "bloom_level": "remember",
                    "source": {
                        "chunk_id": chunk_id,
                        "citation": first_sentence,
                        "evidence_verified": True,
                        "confidence_score": 1.0
                    }
                }
            ]
        }
        return json.dumps(mock_data)


ai_client = AIClient()
