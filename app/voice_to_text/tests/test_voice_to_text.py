
import pytest
from fastapi.testclient import TestClient

from app.voice_to_text.routers import router
from fastapi import FastAPI

from app.voice_to_text.utils import (
    validate_audio_file,
    clean_transcription
)

app = FastAPI()
app.include_router(router)

client = TestClient(app)


# --------------------------------
# 1. Successful transcription test
# --------------------------------

def test_successful_transcription(monkeypatch):

    def mock_transcription(audio_path):
        return {
            "success": True,
            "text": "Create a Python program",
            "language": "en"
        }

    monkeypatch.setattr(
        "app.voice_to_text.routers.transcribe_audio",
        mock_transcription
    )

    response = client.post(
        "/voice-to-text/transcribe",
        files={
            "file": (
                "test.wav",
                b"fake audio content",
                "audio/wav"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["raw_text"] == "Create a Python program"
    assert data["transcribed_text"] == "Create a Python program"
    assert data["language"] == "en"


# --------------------------------
# 2. Empty audio test
# --------------------------------

def test_empty_audio():

    response = client.post(
        "/voice-to-text/transcribe",
        files={
            "file": ("empty.wav", b"", "audio/wav")
        }
    )

    assert response.status_code == 400


# --------------------------------
# 3. Unsupported format test
# --------------------------------

def test_unsupported_format():

    response = client.post(
        "/voice-to-text/transcribe",
        files={
            "file": ("test.txt", b"sample content", "text/plain")
        }
    )

    assert response.status_code == 400


# --------------------------------
# 4. Text cleaning test
# --------------------------------

def test_clean_transcription():

    text = "Um create a Python program uh"

    result = clean_transcription(text)

    assert result == "create a Python program"


# --------------------------------
# 5. Preserve technical words
# --------------------------------

def test_preserve_technical_words():

    text = "Create a Python API using FastAPI"

    result = clean_transcription(text)

    assert result == text


# --------------------------------
# 6. File validation test
# --------------------------------

def test_valid_audio_file(tmp_path):

    audio_file = tmp_path / "sample.wav"

    audio_file.write_bytes(b"sample audio")

    validate_audio_file(str(audio_file))


# --------------------------------
# 7. Missing audio file test
# --------------------------------

def test_missing_audio_file():

    with pytest.raises(ValueError):
        validate_audio_file("missing.wav")
