from fastapi import FastAPI

from app.llm.routers import router as llm_router


app = FastAPI(
    title="CodeMate AI",
    description="AI-powered Coding Assistant",
    version="1.0.0"
)


# LLM module
app.include_router(llm_router)


@app.get("/")
async def home():

    return {
        "message": "CodeMate AI Backend Running",
        "status": "success"
    }