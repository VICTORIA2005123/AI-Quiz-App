from app.models.schemas import QuestionSchema, QuestionType, DifficultyLevel, BloomTaxonomyLevel, SourceCitation, DocumentChunk
from app.services.evidence_verifier import evidence_verifier


def test_evidence_verification_pass_on_authentic_citation():
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        section_title="Neuroscience",
        text="Neurons communicate with each other via electrical events called action potentials and chemical neurotransmitters."
    )

    valid_question = QuestionSchema(
        question_id="q001",
        type=QuestionType.SINGLE_CHOICE,
        question="How do neurons communicate?",
        options=[
            "Via action potentials and chemical neurotransmitters",
            "Exclusively through mechanical vibrations",
            "By direct nuclear fusion",
            "Without any chemical or electrical signals"
        ],
        correct_answer="Via action potentials and chemical neurotransmitters",
        explanation="The source text explicitly confirms action potentials and chemical neurotransmitters.",
        difficulty=DifficultyLevel.MEDIUM,
        bloom_level=BloomTaxonomyLevel.UNDERSTAND,
        source=SourceCitation(
            chunk_id="chunk_001",
            citation="Neurons communicate with each other via electrical events called action potentials",
            evidence_verified=True,
            confidence_score=1.0
        )
    )

    verified_questions, audit = evidence_verifier.verify_quiz_questions([valid_question], [chunk])

    assert audit["passed_grounding"] == 1
    assert audit["failed_grounding"] == 0
    assert verified_questions[0].source.evidence_verified is True
    assert verified_questions[0].source.confidence_score >= 0.8


def test_evidence_verification_fail_on_hallucinated_citation():
    chunk = DocumentChunk(
        chunk_id="chunk_001",
        section_title="Neuroscience",
        text="Neurons communicate with each other via electrical events called action potentials."
    )

    hallucinated_question = QuestionSchema(
        question_id="q002",
        type=QuestionType.SINGLE_CHOICE,
        question="What is the speed of light in deep space vacuum?",
        options=["300000 km/s", "150000 km/s"],
        correct_answer="300000 km/s",
        explanation="Speed of light is constant.",
        difficulty=DifficultyLevel.EASY,
        bloom_level=BloomTaxonomyLevel.REMEMBER,
        source=SourceCitation(
            chunk_id="chunk_001",
            citation="The speed of light in vacuum is exactly 299792458 meters per second.",
            evidence_verified=True,
            confidence_score=1.0
        )
    )

    verified_questions, audit = evidence_verifier.verify_quiz_questions([hallucinated_question], [chunk])

    assert audit["failed_grounding"] == 1
    assert verified_questions[0].source.evidence_verified is False
    assert verified_questions[0].source.confidence_score < 0.65
