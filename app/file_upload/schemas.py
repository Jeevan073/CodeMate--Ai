from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool
    message: str
    file_id: str
    filename: str
    file_type: str
    size_bytes: int
    content: str
    chunks_created: int