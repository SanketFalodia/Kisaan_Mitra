
# text_to_speech_free.py
from gtts import gTTS
import os
import time

async def synthesize_speech(text: str, language: str = "hi", output_path: str = None) -> str:
    """
    Simple TTS using gTTS (Google Text-to-Speech)
    """
    try:
        os.makedirs("temp_audio", exist_ok=True)
        if output_path is None:
            output_path = f"./temp_audio/response_{int(time.time())}.mp3"

        tts = gTTS(text=text, lang=language)
        tts.save(output_path)

        print(f"✅ Audio saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ TTS error: {e}")
        return None

# text_to_speech_free.py
from gtts import gTTS
import os
import time

async def synthesize_speech(text: str, language: str = "hi", output_path: str = None) -> str:
    """
    Simple TTS using gTTS (Google Text-to-Speech)
    """
    try:
        os.makedirs("temp_audio", exist_ok=True)
        if output_path is None:
            output_path = f"./temp_audio/response_{int(time.time())}.mp3"

        tts = gTTS(text=text, lang=language)
        tts.save(output_path)

        print(f"✅ Audio saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ TTS error: {e}")
        return None
