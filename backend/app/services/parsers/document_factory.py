from typing import Dict, Type
from app.services.parsers.base import BaseDocumentParser
from app.services.parsers.pdf_parser import PDFDocumentParser
from app.services.parsers.docx_parser import DocxDocumentParser
from app.services.parsers.text_parser import TextDocumentParser
from app.services.parsers.office_parser import OfficeDocumentParser
from app.services.parsers.image_parser import ImageDocumentParser

PARSER_REGISTRY: Dict[str, Type[BaseDocumentParser]] = {
    "pdf": PDFDocumentParser,
    "docx": DocxDocumentParser,
    "txt": TextDocumentParser,
    "md": TextDocumentParser,
    "markdown": TextDocumentParser,
    "html": TextDocumentParser,
    "htm": TextDocumentParser,
    "pptx": OfficeDocumentParser,
    "xlsx": OfficeDocumentParser,
    "csv": OfficeDocumentParser,
    "png": ImageDocumentParser,
    "jpg": ImageDocumentParser,
    "jpeg": ImageDocumentParser,
}


def get_parser_for_extension(ext: str) -> BaseDocumentParser:
    normalized_ext = ext.lower().lstrip(".")
    parser_cls = PARSER_REGISTRY.get(normalized_ext)
    if not parser_cls:
        raise ValueError(f"No document parser registered for extension '{normalized_ext}'")
    return parser_cls()
