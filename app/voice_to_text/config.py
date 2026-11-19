
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

WHISPER_MODEL = "whisper-large-v3-turbo"

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
