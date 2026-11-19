import logging

from fastapi import APIRouter, HTTPException
from starlette.concurrency import run_in_threadpool

from .schemas import LLMRequest, LLMResponse
from .service import LLMServiceError, llm_service


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/llm",
    tags=["LLM"]
)


async def process_request(payload: LLMRequest):

    try:

        answer = await run_in_threadpool(
            llm_service.respond,
            payload
        )

        return LLMResponse(
            task=payload.task,
            language=payload.language.lower().strip(),
            answer=answer,
            model=llm_service.model
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except LLMServiceError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )

    except Exception as exc:

        logger.exception("Unexpected LLM error")

        raise HTTPException(
            status_code=500,
            detail="Unexpected LLM service error."
        )


@router.post("/generate", response_model=LLMResponse)
async def generate_code(payload: LLMRequest):

    if payload.task != "generate":
        raise HTTPException(
            status_code=422,
            detail="Task must be generate."
        )

    return await process_request(payload)


@router.post("/debug", response_model=LLMResponse)
async def debug_code(payload: LLMRequest):

    if payload.task != "debug":
        raise HTTPException(
            status_code=422,
            detail="Task must be debug."
        )

    return await process_request(payload)


@router.post("/explain", response_model=LLMResponse)
async def explain_code(payload: LLMRequest):

    if payload.task != "explain":
        raise HTTPException(
            status_code=422,
            detail="Task must be explain."
        )

    return await process_request(payload)