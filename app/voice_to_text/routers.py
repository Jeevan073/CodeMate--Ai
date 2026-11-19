
import os
import tempfile
import logging

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Form
)
from starlette.concurrency import run_in_threadpool
from pydantic import ValidationError

from .services import transcribe_audio
from .utils import validate_audio_file, clean_transcription

from app.llm.schemas import LLMRequest, LLMResponse
from app.llm.service import llm_service, LLMServiceError


router = APIRouter(
    prefix="/voice-to-text",
    tags=["Voice-to-Text"]
)

logger = logging.getLogger(__name__)


async def process_audio(file: UploadFile):

    temp_path = None

    try:
        extension = os.path.splitext(file.filename or "")[1].lower()

        if not extension:
            raise HTTPException(
                status_code=400,
                detail="Audio filename must have an extension"
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_path = temp_file.name
            total_size = 0

            while chunk := await file.read(1024 * 1024):

                total_size += len(chunk)

                if total_size > 25 * 1024 * 1024:
                    raise HTTPException(
                        status_code=413,
                        detail="Audio file exceeds 25 MB limit"
                    )

                temp_file.write(chunk)

        validate_audio_file(temp_path)

        result = transcribe_audio(temp_path)

        raw_text = result["text"]
        cleaned_text = clean_transcription(raw_text)

        if not cleaned_text or not cleaned_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No speech detected in audio"
            )

        return {
            "filename": file.filename,
            "raw_text": raw_text,
            "transcribed_text": cleaned_text,
            "language": result["language"]
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        logger.exception("Voice-to-text processing failed")

        raise HTTPException(
            status_code=500,
            detail="Audio transcription failed"
        ) from error

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()


# Existing transcription endpoint
@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...)
):

    result = await process_audio(file)

    return {
        "success": True,
        **result
    }


# New voice + LLM integration endpoint
@router.post("/assist")
async def voice_assistant(
    file: UploadFile = File(...),

    task: str = Form(default="generate"),
    language: str = Form(default="python"),

    code: str | None = Form(default=None),
    file_id: str | None = Form(default=None),

    error_message: str | None = Form(default=None),

    detail_level: str = Form(default="beginner")
):

    try:

        # 1. Convert audio into text
        transcription = await process_audio(file)

        spoken_text = transcription["transcribed_text"]

        # 2. Build existing LLM request
        llm_request = LLMRequest(
            task=task,
            language=language,
            user_input=spoken_text,

            code=(
                code
                or (
                    "Use the uploaded file for analysis."
                    if file_id else None
                )
            ),

            file_id=file_id,
            error_message=error_message,
            detail_level=detail_level
        )

        # 3. Send transcription to existing LLM service
        answer = await run_in_threadpool(
            llm_service.respond,
            llm_request
        )

        # 4. Build LLM response
        llm_response = LLMResponse(
            task=llm_request.task,
            language=llm_request.language.lower().strip(),
            answer=answer,
            model=llm_service.model
        )

        # 5. Return transcription and AI answer
        return {
            "success": True,
            "filename": transcription["filename"],
            "raw_text": transcription["raw_text"],
            "transcribed_text": spoken_text,
            "detected_language": transcription["language"],
            "llm_response": llm_response.model_dump()
        }

    except HTTPException:
        raise

    except ValidationError as error:
        raise HTTPException(
            status_code=422,
            detail=error.errors()
        )

    except LLMServiceError as error:
        logger.exception("Voice LLM processing failed")

        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception as error:
        logger.exception("Voice assistant failed")

        raise HTTPException(
            status_code=500,
            detail="Voice assistant processing failed"
        ) from error
