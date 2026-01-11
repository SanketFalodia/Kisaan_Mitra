# main.py
from fastapi import FastAPI, UploadFile, File
from speech_to_text_free import transcribe_audio_local
from text_to_speech_free import synthesize_speech
from ollama_llm import call_mistral
import os, shutil

app = FastAPI(title="Voice-first AI Assistant")
os.makedirs("temp_audio", exist_ok=True)

@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    # Save uploaded audio
    audio_path = f"temp_audio/{audio.filename}"
    with open(audio_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # STT
    user_text = await transcribe_audio_local(audio_path)
    if not user_text:
        return {"error": "Failed to transcribe audio."}

    # LLM
    bot_text = call_mistral(user_text)

    # TTS
    audio_out = await synthesize_speech(bot_text)
    if not audio_out:
        return {"error": "Failed to generate speech."}

    return {
        "user_text": user_text,
        "bot_text": bot_text,
        "audio_path": audio_out
    }

