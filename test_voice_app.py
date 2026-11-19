from fastapi import FastAPI
from app.voice_to_text.routers import router

app = FastAPI()

app.include_router(router)