from app.services.parsers.text_parser import TextDocumentParser
from app.services.parsers.document_factory import get_parser_for_extension
from app.services.normalizer import normalizer_v1


def test_text_parser():
    parser = TextDocumentParser()
    sample = "# Introduction to Genetics\nDNA carries the genetic instructions for all living organisms."
    text, meta = parser.parse(sample.encode("utf-8"), "genetics.md")

    assert "Introduction to Genetics" in text
    assert meta["format"] == "md"


def test_markdown_normalizer_and_chunker():
    raw_text = """
    # Section 1: Cellular Biology
    Mitochondria are membrane-bound cell organelles that generate chemical energy.
    
    
    * Point 1: Energy generation
    * Point 2: ATP synthesis
    
    ## Section 2: Photosynthesis
    Chloroplasts capture light energy to drive synthesis of sugars.
    """
    normalized = normalizer_v1.normalize_to_markdown(raw_text)
    assert "- Point 1: Energy generation" in normalized
    assert "\n\n\n" not in normalized

    chunks = normalizer_v1.chunk_document(normalized)
    assert len(chunks) >= 1
    assert chunks[0].chunk_id == "chunk_001"
    assert chunks[0].section_title != ""
    assert "Mitochondria" in chunks[0].text


def test_document_factory_resolution():
    assert get_parser_for_extension("pdf") is not None
    assert get_parser_for_extension("docx") is not None
    assert get_parser_for_extension("txt") is not None
    assert get_parser_for_extension("md") is not None
    assert get_parser_for_extension("pptx") is not None
    assert get_parser_for_extension("xlsx") is not None
