from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any


class BaseDocumentParser(ABC):
    @abstractmethod
    def parse(self, content: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parses document bytes into raw text and extraction metadata (page count, OCR confidence, etc.)
        Returns: (extracted_text, metadata_dict)
        """
        pass
