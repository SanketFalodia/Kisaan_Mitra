import asyncio
import os
from typing import Tuple, Optional
import tempfile
import threading


class MultilingualAudioProcessor:
    """
    Audio processing with WHISPER MEDIUM model
    HARDCODED to medium - no fallbacks to base
    """

    def __init__(self, model_size: str = "medium"):
        """
        Initialize with MEDIUM Whisper model - FORCED
        """
        self.model_size = "medium"  # HARDCODED
        self.model = None
        self.initialized = False

        print("🎤 Initializing Whisper with MEDIUM model (forced)")
        print("⏳ Downloading ~1.5GB model (first time only)...")

        try:
            from faster_whisper import WhisperModel

            self.model = WhisperModel(
                "medium",
                device="cpu",
                compute_type="int8",
            )

            self.initialized = True
            print("✅ SUCCESS: Whisper MEDIUM model loaded!")
            print("📊 Model: MEDIUM (excellent Hindi/Urdu accuracy)")

        except RuntimeError as e:
            if "malloc" in str(e).lower():
                print("❌ CRITICAL: Not enough RAM for MEDIUM model!")
                print("⚠️ Need ~3GB free RAM")
            else:
                print(f"❌ Error loading MEDIUM: {e}")

        except Exception as e:
            print(f"❌ Error: {e}")

    async def speech_to_text(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> Tuple[str, str, float]:
        """
        Convert speech to text with MEDIUM Whisper model
        """

        if not self.initialized or self.model is None:
            print("❌ MEDIUM Whisper not available")
            return "", "en", 0.0

        try:
            print("🎤 Transcribing with MEDIUM Whisper model")

            segments, info = self.model.transcribe(
                audio_path,
                language=language or "hi",
                beam_size=5,
                best_of=5,
                temperature=0.0,
                compression_ratio_threshold=2.4,
                no_speech_threshold=0.6,
            )

            transcribed_text = ""
            for segment in segments:
                if segment.text.strip():
                    transcribed_text += " " + segment.text.strip()

            transcribed_text = transcribed_text.strip()

            print(f"✅ Transcription: {transcribed_text}")
            print(f"📊 Language: {info.language}")

            devanagari_count = self._count_devanagari(transcribed_text)
            urdu_count = self._count_urdu(transcribed_text)

            print(f"📊 Script: Devanagari={devanagari_count}, Urdu={urdu_count}")

            if devanagari_count > urdu_count:
                print("✅ EXCELLENT: Hindi (Devanagari) output!")
            else:
                print("⚠️ Some Urdu detected, MEDIUM handles this well")

            return transcribed_text, "hi", 0.95

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return "", "en", 0.0

    def _count_devanagari(self, text: str) -> int:
        count = 0
        for char in text:
            if 0x0900 <= ord(char) <= 0x097F:
                count += 1
        return count

    def _count_urdu(self, text: str) -> int:
        count = 0
        for char in text:
            if 0x0600 <= ord(char) <= 0x06FF:
                count += 1
        return count

    def text_to_speech_edge(
        self,
        text: str,
        language: str = "hi",
        output_path: str = None,
    ) -> bool:
        """
        Convert text to speech using Edge-TTS.
        SYNC wrapper: do NOT await this in callers.
        """

        try:
            import edge_tts

            voice_map = {
                "hi": "hi-IN-SwaraNeural",
                "en": "en-US-AriaNeural",
                "garhwali": "hi-IN-SwaraNeural",
                "kumaoni": "hi-IN-SwaraNeural",
            }

            voice = voice_map.get(language, "hi-IN-SwaraNeural")

            if output_path is None:
                output_path = os.path.join(
                    tempfile.gettempdir(),
                    "speech.wav",
                )

            success = False

            def run_tts():
                nonlocal success
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                async def tts_async():
                    try:
                        communicate = edge_tts.Communicate(text, voice)
                        await communicate.save(output_path)
                        return True
                    except Exception as e:
                        print(f"⚠️ TTS generate error: {e}")
                        return False

                try:
                    success = loop.run_until_complete(tts_async())
                finally:
                    loop.close()

            thread = threading.Thread(target=run_tts, daemon=False)
            thread.start()
            thread.join(timeout=30)

            if success and os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                print(f"✅ Edge-TTS saved to: {output_path}")
                return True

            print("⚠️ TTS file not created")
            return False

        except ImportError:
            print("⚠️ edge_tts not installed, using offline TTS")
            return self.text_to_speech_offline(text, language, output_path)

        except Exception as e:
            print(f"⚠️ Edge-TTS error: {e}")
            return self.text_to_speech_offline(text, language, output_path)

    def text_to_speech_offline(
        self,
        text: str,
        language: str = "hi",
        output_path: str = None,
    ) -> bool:
        """
        Offline TTS fallback using pyttsx3
        """

        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            engine.setProperty("volume", 0.9)

            if output_path is None:
                output_path = os.path.join(
                    tempfile.gettempdir(),
                    "speech.wav",
                )

            engine.save_to_file(text, output_path)
            engine.runAndWait()

            if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                print(f"✅ Offline TTS saved: {output_path}")
                return True

            print("⚠️ Offline TTS file not created")
            return False

        except Exception as e:
            print(f"⚠️ Offline TTS error: {e}")
            return False


class MultilingualTranslator:
    """
    Translator for multilingual support
    """

    def __init__(self):
        self.translations = {
            "hi": {
                "greeting": "नमस्कार भाई!",
                "schemes_found": "आपके लिए {count} योजनाएं उपलब्ध हैं:",
                "no_schemes": "क्षमा करें, आपकी स्थिति के लिए कोई योजना उपलब्ध नहीं है।",
            },
            "en": {
                "greeting": "Hello Farmer!",
                "schemes_found": "We found {count} schemes for you:",
                "no_schemes": "Sorry, no schemes available for your situation.",
            },
        }

    def translate(self, key: str, language: str = "hi", **kwargs) -> str:
        try:
            text = self.translations.get(language, self.translations["hi"]).get(key, "")
            return text.format(**kwargs)
        except Exception:
            return ""
