from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile, HTTPException

from app.file_upload.schemas import UploadResponse


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Uploaded files storage
UPLOAD_DIR = BASE_DIR / "uploaded_files"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Supported coding and text file formats
ALLOWED_EXTENSIONS = {
    ".py",
    ".c",
    ".cpp",
    ".h",
    ".java",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".sql",
    ".txt",
    ".md",
    ".json",
    ".xml",
    ".yaml",
    ".yml"
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

MAX_CONTENT_LENGTH = 100_000


async def process_upload(file: UploadFile):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    # Validate extension
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {extension}"
        )

    # Read file
    file_content = await file.read(MAX_FILE_SIZE + 1)

    # Validate file size
    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 5 MB limit."
        )

    # Decode file content
    try:
        extracted_content = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Unable to read file. Please upload a UTF-8 text file."
        )

    # Generate unique file ID
    file_id = uuid4().hex

    # Store using generated filename
    stored_filename = f"{file_id}{extension}"
    file_path = UPLOAD_DIR / stored_filename

    try:
        file_path.write_bytes(file_content)
    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Unable to save uploaded file."
        )

    # Prepare response
    return UploadResponse(
        success=True,
        message="File uploaded and processed successfully.",
        file_id=file_id,
        filename=Path(file.filename).name,
        file_type=extension,
        size_bytes=len(file_content),
        content=extracted_content[:MAX_CONTENT_LENGTH]
    )