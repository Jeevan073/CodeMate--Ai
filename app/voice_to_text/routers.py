
import os
import tempfile
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

from .services import transcribe_audio
from .utils import validate_audio_file, clean_transcription

router = APIRouter(
    prefix="/voice-to-text",
    tags=["Voice-to-Text"]
)

logger = logging.getLogger(__name__)


@router.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):

    temp_path = None

    try:
        # Check file extension
        extension = os.path.splitext(file.filename or "")[1].lower()

        if not extension:
            raise HTTPException(
                status_code=400,
                detail="Audio filename must have an extension"
            )

        # Save uploaded audio temporarily
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

        # Validate audio file
        validate_audio_file(temp_path)

        # Transcribe using local Whisper
        result = transcribe_audio(temp_path)

        raw_text = result["text"]

        # Clean transcription
        cleaned_text = clean_transcription(raw_text)

        return {
            "success": True,
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

    except Exception:
        logger.exception("Voice-to-text processing failed")

        raise HTTPException(
            status_code=500,
            detail="Audio transcription failed"
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()
