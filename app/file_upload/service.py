
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile, HTTPException

from app.file_upload.schemas import UploadResponse
from app.rag.upload_ingestion import uploaded_code_indexer


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

    # 1. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    original_filename = Path(file.filename).name
    extension = Path(original_filename).suffix.lower()

    # 2. Validate extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {extension}"
        )

    # 3. Read file
    file_content = await file.read(MAX_FILE_SIZE + 1)

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # 4. Validate file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 5 MB limit."
        )

    # 5. Decode file content
    try:
        extracted_content = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Unable to read file. Please upload a UTF-8 text file."
        )

    # 6. Generate unique file ID
    file_id = uuid4().hex

    # 7. Save uploaded file
    stored_filename = f"{file_id}{extension}"
    file_path = UPLOAD_DIR / stored_filename

    try:
        file_path.write_bytes(file_content)

    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to save uploaded file."
        ) from exc

    # 8. Index uploaded code into existing ChromaDB
    try:
        indexing_result = uploaded_code_indexer.ingest_uploaded_file(
            file_id=file_id,
            file_path=str(file_path),
            original_filename=original_filename
        )

    except Exception as exc:

        # Remove the saved file if indexing fails
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="File uploaded but RAG indexing failed."
        ) from exc

    # 9. Prepare API response
    return UploadResponse(
        success=True,
        message="File uploaded and processed successfully.",
        file_id=file_id,
        filename=original_filename,
        file_type=extension,
        size_bytes=len(file_content),
        content=extracted_content[:MAX_CONTENT_LENGTH],
        chunks_created=indexing_result["chunks_created"]
    )
