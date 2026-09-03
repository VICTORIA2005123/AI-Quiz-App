import io
import zipfile
import pytest
from fastapi import HTTPException
from app.security.file_security import inspect_file_content_and_magic_bytes, secure_shred_file


def test_valid_pdf_magic_bytes():
    valid_pdf = b"%PDF-1.7\nSample content"
    inspect_file_content_and_magic_bytes(valid_pdf, "pdf")


def test_corrupted_pdf_magic_bytes():
    corrupted = b"NOT_A_PDF_HEADER"
    with pytest.raises(HTTPException) as exc_info:
        inspect_file_content_and_magic_bytes(corrupted, "pdf")
    assert exc_info.value.status_code == 400
    assert "magic byte signature" in exc_info.value.detail


def test_empty_file_rejected():
    with pytest.raises(HTTPException) as exc_info:
        inspect_file_content_and_magic_bytes(b"", "txt")
    assert exc_info.value.status_code == 400
    assert "empty" in exc_info.value.detail


def test_oversized_file_rejected():
    oversized = b"A" * (27 * 1024 * 1024)  # 27 MB (> 25 MB limit)
    with pytest.raises(HTTPException) as exc_info:
        inspect_file_content_and_magic_bytes(oversized, "txt")
    assert exc_info.value.status_code == 413
    assert "exceeds maximum allowed size" in exc_info.value.detail


def test_zip_bomb_defense_for_docx():
    # Construct a high compression ratio payload
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("large_file.xml", b"0" * (51 * 1024 * 1024))  # 51MB uncompressed
    compressed_bytes = buf.getvalue()

    with pytest.raises(HTTPException) as exc_info:
        inspect_file_content_and_magic_bytes(compressed_bytes, "docx")
    assert exc_info.value.status_code == 400
    assert "decompression bomb" in exc_info.value.detail or "ratio" in exc_info.value.detail


def test_secure_shredding(tmp_path):
    temp_file = tmp_path / "sensitive.txt"
    temp_file.write_text("Confidential study notes")
    assert temp_file.exists()
    secure_shred_file(str(temp_file))
    assert not temp_file.exists()
