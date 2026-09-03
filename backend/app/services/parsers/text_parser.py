from typing import Tuple, Dict, Any
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from app.services.parsers.base import BaseDocumentParser


class TextDocumentParser(BaseDocumentParser):
    def parse(self, content: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
        
        try:
            raw_str = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                raw_str = content.decode("latin-1")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unable to decode text file: {str(e)}"
                )

        if ext in {"html", "htm"}:
            soup = BeautifulSoup(raw_str, "html.parser")
            # Remove scripts and styles
            for script_or_style in soup(["script", "style", "meta", "noscript"]):
                script_or_style.extract()
            text = soup.get_text(separator="\n\n").strip()
        else:
            text = raw_str.strip()

        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text document contains no extractable content."
            )

        return text, {
            "format": ext,
            "char_count": len(text)
        }
