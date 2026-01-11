# speech_to_text_free.py
'''
import whisper
import torch
import librosa

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🎤 STT using device: {device}")

whisper_model = None

def load_whisper():
    global whisper_model
    if whisper_model is None:
        print("⏳ Loading Whisper LARGE-V3...")
        whisper_model = whisper.load_model("large-v3", device=device)
    return whisper_model

async def transcribe_audio_local(audio_path: str) -> str:
    """
    Transcribe audio using Whisper LARGE-V3
    """
    try:
        model = load_whisper()
        print("🎤 Transcribing with Whisper LARGE-V3...")
        result = model.transcribe(audio_path, language="hi", fp16=(device=="cuda"))
        text = result.get("text", "").strip()
        print(f"✅ Transcribed Text: {text}")
        return text
    except Exception as e:
        print(f"❌ STT error: {e}")
        return None
'''
# Add at top of speech_to_text_free.py
import subprocess
import os

async def convert_ogg_to_wav(ogg_path: str) -> str:
    """Convert WhatsApp OGG to WAV for Whisper"""
    wav_path = ogg_path.replace('.ogg', '.wav')
    if os.path.exists(wav_path):
        return wav_path
    
    cmd = [
        'ffmpeg', '-i', ogg_path, 
        '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le',
        wav_path, '-y'
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Converted {ogg_path} → {wav_path}")
        return wav_path
    except Exception as e:
        print(f"❌ OGG conversion failed: {e}")
        return ogg_path  # Fallback

async def transcribe_audio_local(audio_path: str) -> str:
    """Enhanced - handles OGG + WAV"""
    # Convert OGG if needed
    if audio_path.endswith('.ogg'):
        audio_path = await convert_ogg_to_wav(audio_path)
    
    # Original Whisper code...
    load_whisper()
    result = whisper_model.transcribe(audio_path, language="hi")
    return result["text"].strip()

import whisper
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
whisper_model = None

def load_whisper():
    global whisper_model
    if whisper_model is None:
        whisper_model = whisper.load_model("large-v3", device=device)

async def transcribe_audio_local(audio_path: str) -> str:
    load_whisper()
    result = whisper_model.transcribe(
        audio_path,
        language="hi",
        fp16=(device == "cuda")
    )
    return result["text"].strip()
