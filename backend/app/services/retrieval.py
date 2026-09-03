from typing import List
from app.models.schemas import DocumentChunk
from app.core.config import settings


class RetrievalTokenBudgeter:
    """
    Manages AI token budget and selects the optimal set of chunks to satisfy
    the target question count without exceeding token caps.
    """
    def __init__(self, max_tokens: int = settings.MAX_AI_TOKENS_PER_JOB):
        self.max_tokens = max_tokens

    def estimate_tokens(self, input_val) -> int:
        # Standard heuristic: 1 token ≈ 4 characters
        if isinstance(input_val, int):
            return input_val // 4 + 1
        return len(str(input_val)) // 4 + 1

    def select_chunks_for_quiz(self, chunks: List[DocumentChunk], target_question_count: int) -> List[DocumentChunk]:
        if not chunks:
            return []

        # If all chunks comfortably fit in budget, return all
        total_chars = sum(len(c.text) for c in chunks)
        if self.estimate_tokens(total_chars) <= self.max_tokens:
            return chunks

        # Otherwise, calculate how many chunks are needed (e.g. ~1-2 questions per chunk)
        needed_chunks_count = min(len(chunks), max(3, target_question_count + 1))
        
        # Select evenly distributed chunks across the document to provide broad coverage
        step = max(1, len(chunks) // needed_chunks_count)
        selected_indices = list(range(0, len(chunks), step))[:needed_chunks_count]
        selected_chunks = [chunks[i] for i in selected_indices]

        # Ensure selected chunks stay within token budget
        budgeted_chunks = []
        current_token_count = 0
        for chunk in selected_chunks:
            tokens = self.estimate_tokens(chunk.text)
            if current_token_count + tokens <= self.max_tokens:
                budgeted_chunks.append(chunk)
                current_token_count += tokens
            else:
                break

        return budgeted_chunks if budgeted_chunks else chunks[:1]


retrieval_budgeter = RetrievalTokenBudgeter()
