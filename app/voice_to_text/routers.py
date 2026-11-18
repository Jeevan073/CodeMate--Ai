from fastapi import APIRouter, UploadFile, File
from groq import Groq
router=APIRouter()
client=Groq(api_key="YOUR_GROQ_API_KEY")
@router.post("/voice-to-text")
async def voice_to_text(audio: UploadFile=File(...)):
    audio_bytes=await audio.read()
    transcription=client.audio.transcriptions.create(
        file=(audio.filename, audio_bytes),
        model="whisper-large-v3-turbo"
    )
    return{"text":transcription.text}
