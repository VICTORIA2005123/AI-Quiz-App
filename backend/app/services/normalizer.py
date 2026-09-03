import re
from typing import List, Tuple
from app.models.schemas import DocumentChunk
from app.core.config import settings

NORMALIZER_VERSION = "v1"


class MarkdownNormalizerV1:
    """
    Normalizes extracted raw document text into standardized markdown hierarchy
    and chunks the content into structured, indexed chunks with Chunk IDs.
    """
    def __init__(self, target_chunk_chars: int = 2500, chunk_overlap_chars: int = 300):
        self.target_chunk_chars = target_chunk_chars
        self.chunk_overlap_chars = chunk_overlap_chars

    def normalize_to_markdown(self, raw_text: str) -> str:
        if not raw_text:
            return ""

        # Normalize line endings
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

        # Strip whitespace on empty/blank lines
        text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)

        # Replace excessive blank lines (> 2 newlines -> 2 newlines)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Standardize bullet list characters (*, +, • -> -)
        text = re.sub(r"^[ \t]*[•*+][ \t]+", "- ", text, flags=re.MULTILINE)

        # Ensure header lines have a space after '#'
        text = re.sub(r"^(#{1,6})([^# \n])", r"\1 \2", text, flags=re.MULTILINE)

        # Strip trailing whitespace on each line
        lines = [line.rstrip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    def chunk_document(self, markdown_text: str) -> List[DocumentChunk]:
        normalized = self.normalize_to_markdown(markdown_text)
        if not normalized:
            return []

        # Split by markdown headers or double line breaks
        sections = re.split(r"\n(?=#{1,4}\s+)", normalized)
        chunks: List[DocumentChunk] = []
        chunk_index = 1
        current_char_offset = 0

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Extract header title if present
            header_match = re.match(r"^#{1,4}\s+(.+)$", section, flags=re.MULTILINE)
            section_title = header_match.group(1).strip() if header_match else "General Overview"

            # If section fits within target size
            if len(section) <= self.target_chunk_chars + self.chunk_overlap_chars:
                chunk_id = f"chunk_{chunk_index:03d}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    section_title=section_title,
                    text=section,
                    start_char=current_char_offset,
                    end_char=current_char_offset + len(section),
                    word_count=len(section.split())
                ))
                chunk_index += 1
                current_char_offset += len(section)
            else:
                # Sub-divide large section into overlapping windows
                paragraphs = section.split("\n\n")
                current_sub_chunk = []
                current_len = 0

                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue

                    if current_len + len(para) > self.target_chunk_chars and current_sub_chunk:
                        chunk_text = "\n\n".join(current_sub_chunk)
                        chunk_id = f"chunk_{chunk_index:03d}"
                        chunks.append(DocumentChunk(
                            chunk_id=chunk_id,
                            section_title=section_title,
                            text=chunk_text,
                            start_char=current_char_offset,
                            end_char=current_char_offset + len(chunk_text),
                            word_count=len(chunk_text.split())
                        ))
                        chunk_index += 1
                        current_char_offset += len(chunk_text)

                        # Keep overlap paragraph if available
                        current_sub_chunk = [current_sub_chunk[-1], para] if len(current_sub_chunk) > 1 else [para]
                        current_len = sum(len(p) for p in current_sub_chunk)
                    else:
                        current_sub_chunk.append(para)
                        current_len += len(para)

                if current_sub_chunk:
                    chunk_text = "\n\n".join(current_sub_chunk)
                    chunk_id = f"chunk_{chunk_index:03d}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        section_title=section_title,
                        text=chunk_text,
                        start_char=current_char_offset,
                        end_char=current_char_offset + len(chunk_text),
                        word_count=len(chunk_text.split())
                    ))
                    chunk_index += 1
                    current_char_offset += len(chunk_text)

            if len(chunks) >= settings.MAX_CHUNKS_PER_DOC:
                chunks = chunks[:settings.MAX_CHUNKS_PER_DOC]
                break

        return chunks


normalizer_v1 = MarkdownNormalizerV1()
