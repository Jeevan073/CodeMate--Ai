from fastapi import APIRouter, UploadFile, File
from groq import Groq
router=APIRouter()
client=Groq(api_key="YOUR_GROQ_API_KEY")
def clean_and_analyze_text(text):
    words=text.lower().split()
    filler_words=["like","please","actually","basically","so","just"]
    clean_words = []
    for w in words:
        if w not in filler_words:
            clean_words.append(w)
    cleaned=" ".join(clean_words)
    languages=["python","java","c++","c","html","css","javascript","sql"]
    detected_lang="general"
    for lang in languages:
        if lang in clean_words:
            detected_lang=lang
            break
    if "error" in clean_words or "bug" in clean_words or "fix" in clean_words:
        intent="debugging"
    elif "explain" in clean_words:
        intent="explanation"
    else:
        intent="code_generation"
    return cleaned, detected_lang, intent
@router.post("/voice-to-text")
async def voice_to_text(audio: UploadFile = File(...)):
    audio_bytes=await audio.read()
    transcription=client.audio.transcriptions.create(
        file=(audio.filename, audio_bytes),
        model="whisper-large-v3-turbo"
    )
    cleaned_text,language,intent=clean_and_analyze_text(transcription.text)
    return {
        "raw_text":transcription.text,
        "text":cleaned_text,
        "language":language,
        "intent":intent
    }
