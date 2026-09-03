import io
from typing import Tuple, Dict, Any
from pypdf import PdfReader
from fastapi import HTTPException, status
from app.services.parsers.base import BaseDocumentParser
from app.core.config import settings


class PDFDocumentParser(BaseDocumentParser):
    def parse(self, content: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        try:
            reader = PdfReader(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse PDF document (corrupted or invalid format): {str(e)}"
            )

        if reader.is_encrypted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password-protected or encrypted PDF documents are not supported."
            )

        page_count = len(reader.pages)
        if page_count > settings.MAX_DOCUMENT_PAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDF has {page_count} pages, which exceeds the maximum limit of {settings.MAX_DOCUMENT_PAGES} pages."
            )

        extracted_pages = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_pages.append(f"--- Page {idx + 1} ---\n{page_text}")

        full_text = "\n\n".join(extracted_pages).strip()
        if not full_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF contains no extractable text (it may be a scanned image-only PDF)."
            )

        return full_text, {
            "page_count": page_count,
            "format": "pdf",
            "extracted_pages_count": len(extracted_pages)
        }
