# test_pipeline.py
import asyncio
from speech_to_text_free import transcribe_audio_local
from text_to_speech_free import synthesize_speech
from ollama_llm import call_mistral

async def main():
    audio_path = "temp_audio/sample.wav"  # Put your test audio here

    # 1️⃣ STT
    print("🎤 Transcribing audio...")
    text = await transcribe_audio_local(audio_path)
    print("User Text:", text)

    # 2️⃣ LLM
    print("🧠 Getting response from Mistral...")
    response = call_mistral(text)
    print("Bot Text:", response)

    # 3️⃣ TTS
    print("🔊 Generating speech...")
    audio_out = await synthesize_speech(response)
    print("Audio saved at:", audio_out)

asyncio.run(main())
