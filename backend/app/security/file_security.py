import io
import os
import zipfile
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

# Recognized magic byte signatures
MAGIC_SIGNATURES = {
    "pdf": [b"%PDF-"],
    "docx": [b"PK\x03\x04", b"PK\x05\x06"],
    "pptx": [b"PK\x03\x04", b"PK\x05\x06"],
    "xlsx": [b"PK\x03\x04", b"PK\x05\x06"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
}

# Supported file extensions
SUPPORTED_EXTENSIONS = {"pdf", "docx", "pptx", "xlsx", "csv", "txt", "md", "markdown", "html", "htm", "png", "jpg", "jpeg"}

MAX_UNCOMPRESSED_ZIP_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_ZIP_ENTRIES = 2000
MAX_COMPRESSION_RATIO = 100.0


def validate_file_metadata(file: UploadFile) -> Tuple[str, str]:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file has no filename."
        )
    
    filename = os.path.basename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    
    return filename, ext


def inspect_file_content_and_magic_bytes(content: bytes, ext: str) -> None:
    # 1. Size check
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )
    
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    # 2. Magic byte check
    if ext in MAGIC_SIGNATURES:
        signatures = MAGIC_SIGNATURES[ext]
        if not any(content.startswith(sig) for sig in signatures):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File content does not match expected {ext.upper()} magic byte signature (corrupted or spoofed format)."
            )

    # 3. Zip bomb & malformed archive check for ZIP-based formats (DOCX, PPTX, XLSX)
    if ext in {"docx", "pptx", "xlsx"}:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                total_uncompressed = 0
                entry_count = len(zf.infolist())
                if entry_count > MAX_ZIP_ENTRIES:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Archive contains too many entries (potential zip bomb attack)."
                    )
                for info in zf.infolist():
                    total_uncompressed += info.file_size
                    if total_uncompressed > MAX_UNCOMPRESSED_ZIP_SIZE:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Uncompressed document size exceeds safe threshold (decompression bomb protection)."
                        )
                if len(content) > 0 and (total_uncompressed / len(content)) > MAX_COMPRESSION_RATIO:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Abnormal compression ratio detected (potential zip bomb attack)."
                    )
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Malformed or corrupted {ext.upper()} archive file."
            )

    # 4. Text/Markdown UTF-8 validation
    if ext in {"txt", "md", "markdown", "csv", "html", "htm"}:
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content.decode("latin-1")
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Text file encoding is invalid or corrupted."
                )


def secure_shred_file(file_path: str) -> None:
    """Overwrites file with zeros before unlinking to guarantee ephemeral destruction."""
    try:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            with open(file_path, "wb") as f:
                f.write(b"\x00" * min(size, 1024 * 1024))
            os.remove(file_path)
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
