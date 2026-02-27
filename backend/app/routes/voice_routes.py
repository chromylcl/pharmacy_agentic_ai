from fastapi import APIRouter, UploadFile, File
from app.services.whisper_service import transcribe_audio
from app.agents.langchain_agent import run_agent

router = APIRouter()


@router.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):

    # Speech → Text
    text = transcribe_audio(audio)

    # Agent reasoning
    response = run_agent(text)

    return {
        "transcription": text,
        "response": response
    }