
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.retriever import CodeRetriever

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])

# Shared retriever instance
retriever = CodeRetriever()

class RAGRequest(BaseModel):
    query: str = Field(..., min_length=1)
    language: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    file_id: str | None = None


class RAGResponse(BaseModel):
    success: bool
    query: str
    retrieved_chunks: int
    results: list[dict]


@router.post("/retrieve", response_model=RAGResponse)
async def retrieve_context(payload: RAGRequest):

    try:
        results = retriever.retrieve(
            query=payload.query,
            language=payload.language,
            top_k=payload.top_k,
            file_id=payload.file_id
        )

        return RAGResponse(
            success=True,
            query=payload.query,
            retrieved_chunks=len(results),
            results=results
        )

    except Exception as exc:
        logger.exception("RAG retrieval failed")
        raise HTTPException(
            status_code=500,
            detail="RAG retrieval failed."
        ) from exc
