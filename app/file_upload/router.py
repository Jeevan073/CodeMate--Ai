from fastapi import APIRouter, UploadFile, File

from app.file_upload.service import process_upload
from app.file_upload.schemas import UploadResponse


router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):

    result = await process_upload(file)

    return result