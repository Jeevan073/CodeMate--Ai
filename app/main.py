
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.llm.routers import router as llm_router
from app.voice_to_text.routers import router as voice_router
from app.rag.router import router as rag_router
from app.file_upload.router import router as file_upload_router


app = FastAPI(
    title="CodeMate AI",
    description="AI-powered Coding Assistant",
    version="1.0.0"
)

# The Vite frontend runs on a separate origin during development. Keep the
# default local origins usable and allow deployments to supply their own list.
cors_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    # Vite may use a different port for preview or when its default port is
    # occupied. Allow local development origins on any port; production
    # frontend origins should be listed in CORS_ORIGINS above.
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
