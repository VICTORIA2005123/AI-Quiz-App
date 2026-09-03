import csv
import io
import json
from typing import List
from app.models.schemas import QuestionSchema, QuizSchema


class QuizExporter:
    """
    Exports generated quizzes to multiple educational formats:
    - Anki deck TSV/APKG format
    - CSV spreadsheet
    - Markdown study sheet with citations
    - Standard JSON
    """
    @staticmethod
    def export_to_anki_tsv(questions: List[QuestionSchema]) -> str:
        output = io.StringIO()
        writer = csv.writer(output, delimiter="\t")
        for q in questions:
            front = f"<b>{q.question}</b><br><br>" + "<br>".join([f"• {opt}" for opt in q.options])
            back = f"<b>Correct Answer:</b> {q.correct_answer}<br><br><b>Explanation:</b> {q.explanation}<br><br><i>Source Citation:</i> {q.source.citation}"
            writer.writerow([front, back, f"difficulty:{q.difficulty.value}", f"bloom:{q.bloom_level.value}"])
        return output.getvalue()

    @staticmethod
    def export_to_csv(questions: List[QuestionSchema]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Question ID", "Question", "Options", "Correct Answer", "Explanation", "Difficulty", "Bloom Level", "Source Chunk", "Citation"])
        for q in questions:
            writer.writerow([
                q.question_id,
                q.question,
                " | ".join(q.options),
                q.correct_answer,
                q.explanation,
                q.difficulty.value,
                q.bloom_level.value,
                q.source.chunk_id,
                q.source.citation
            ])
        return output.getvalue()

    @staticmethod
    def export_to_markdown_study_guide(quiz: QuizSchema) -> str:
        lines = [
            f"# Study Guide & Quiz: {quiz.title}",
            f"**Source Document:** {quiz.document_name} | **Difficulty:** {quiz.difficulty} | **Questions:** {quiz.question_count}",
            "",
            "---",
            ""
        ]
        for idx, q in enumerate(quiz.questions, 1):
            lines.append(f"### Question {idx}: {q.question}")
            for opt in q.options:
                marker = "[x]" if opt == q.correct_answer else "[ ]"
                lines.append(f"- {marker} {opt}")
            lines.append("")
            lines.append(f"> **Correct Answer:** {q.correct_answer}")
            lines.append(f"> **Explanation:** {q.explanation}")
            lines.append(f"> **Source [{q.source.chunk_id}]:** *\"{q.source.citation}\"* (Grounding Confidence: {int(q.source.confidence_score*100)}%)")
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)


quiz_exporter = QuizExporter()
