
import whisper
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

MODEL_NAME = "small"


@lru_cache(maxsize=1)
def load_whisper_model():
    """Load Whisper model once and reuse it."""
    try:
        logger.info("Loading Whisper model: %s", MODEL_NAME)
        model = whisper.load_model(MODEL_NAME)
        logger.info("Whisper model loaded successfully")
        return model

    except Exception:
        logger.exception("Failed to load Whisper model")
        raise


def transcribe_audio(audio_path: str) -> dict:
    """Convert audio into text using local Whisper."""

    try:
        model = load_whisper_model()

        result = model.transcribe(
            audio_path,
            fp16=False,
            task="transcribe"
        )

        return {
            "success": True,
            "text": result["text"].strip(),
            "language": result.get("language"),
        }

    except Exception:
        logger.exception("Audio transcription failed")
        raise
