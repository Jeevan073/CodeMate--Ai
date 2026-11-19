
import os
import re
from pathlib import Path

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB

ALLOWED_AUDIO_FORMATS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".webm",
    ".mpeg",
    ".mpga",
    ".ogg",
    ".flac"
}

FILLER_WORDS = {
    "um",
    "uh",
    "erm",
    "hmm"
}


def validate_audio_file(file_path: str) -> None:
    """Validate audio file existence, size and extension."""

    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise ValueError("Audio file does not exist")

    if path.suffix.lower() not in ALLOWED_AUDIO_FORMATS:
        raise ValueError("Unsupported audio format")

    if path.stat().st_size == 0:
        raise ValueError("Audio file is empty")

    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("Audio file exceeds 25 MB limit")


def clean_transcription(text: str) -> str:
    """Remove unnecessary filler words without changing meaning."""

    if not text:
        return ""

    cleaned_words = []

    for word in text.split():
        if word.lower().strip(".,!?") not in FILLER_WORDS:
            cleaned_words.append(word)

    cleaned_text = " ".join(cleaned_words)

    cleaned_text = re.sub(r"\s+([.,!?])", r"\1", cleaned_text)
    cleaned_text = re.sub(r"\s{2,}", " ", cleaned_text)

    return cleaned_text.strip()
