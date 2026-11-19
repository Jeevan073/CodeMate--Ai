
from fastapi import FastAPI
from app.llm.routers import router as llm_router
from app.voice_to_text.routers import router as voice_router
from app.rag.router import router as rag_router
from app.file_upload.router import router as file_upload_router


app = FastAPI(
    title="CodeMate AI",
    description="AI-powered Coding Assistant",
    version="1.0.0"
)

app.include_router(llm_router)
app.include_router(voice_router)
app.include_router(rag_router)
app.include_router(
    file_upload_router,
    prefix="/api/files",
    tags=["File Upload"]
)


@app.get("/")
async def home():
    return {
        "message": "CodeMate AI Backend Running",
        "status": "success"
    }
