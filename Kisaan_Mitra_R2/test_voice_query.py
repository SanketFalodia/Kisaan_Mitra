
# test_voice_query

import asyncio
from ollama_llm import call_mistral
from text_to_speech_free import synthesize_speech

async def main():
    text = "मेरी फसल बाढ़ में खराब हो गई है, कृपया मुझे संबंधित सरकारी योजनाओं के बारे में बताइए।"

    print("🧠 Sending text to Ollama...")
    bot_text = call_mistral(text)
    print("Bot Text:", bot_text)

    print("🔊 Generating voice...")
    audio_path = await synthesize_speech(bot_text)

    print("✅ Voice saved at:", audio_path)

asyncio.run(main())

