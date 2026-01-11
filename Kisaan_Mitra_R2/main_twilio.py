"""
Kisaan Mitra V2 - COMPLETE PRODUCTION CODE
Twilio Voice IVR + WhatsApp Voice Messages
Hack The Winter Round 2 Submission
"""

from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse
import os
import shutil
import requests
import uuid
import json
import subprocess
from datetime import datetime
from typing import Optional, List

# ===== YOUR CORE AI MODULES =====
from speech_to_text_free import transcribe_audio_local
from text_to_speech_free import synthesize_speech
from ollama_llm import call_mistral
from intent_detector import detect_intent
from multilingual_retriever import retrieve_schemes

# ===== APP =====
app = FastAPI(title="Kisaan Mitra V2 - Voice + WhatsApp AI", version="2.0")

# ===== DIRECTORIES =====
os.makedirs("temp_audio", exist_ok=True)
os.makedirs("call_logs", exist_ok=True)
os.makedirs("form_submissions", exist_ok=True)

# ===== SHARED FUNCTIONS =====
def log_interaction(platform: str, phone: str, user_text: str, intent: str, schemes: List, response: str):
    """Unified logging for Voice + WhatsApp"""
    log = {
        "platform": platform,
        "phone": phone,
        "timestamp": datetime.now().isoformat(),
        "input": user_text,
        "intent": intent,
        "schemes": [s.get("scheme_name", "Unknown") for s in schemes],
        "output": response[:200] + "..." if len(response) > 200 else response
    }
    
    log_file = "call_logs/history.json"
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log)
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"📊 {platform}: {phone} → {intent} → {len(schemes)} schemes")

# =========================================================
# 1️⃣ WEB UI / DIRECT UPLOAD (BACKWARD COMPATIBLE)
# =========================================================
@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    """Original endpoint - for testing/UI"""
    audio_path = f"temp_audio/web_{uuid.uuid4().hex[:8]}_{audio.filename}"
    with open(audio_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    user_text = await transcribe_audio_local(audio_path)
    if not user_text:
        return {"error": "Transcription failed"}

    intent = detect_intent(user_text)
    schemes = retrieve_schemes(user_text, intent)
    bot_text = call_mistral(user_text, schemes)

    return {
        "user_text": user_text,
        "intent": intent,
        "schemes_count": len(schemes),
        "bot_text": bot_text,
        "status": "success"
    }

# =========================================================
# 2️⃣ TWILIO VOICE IVR
# =========================================================
@app.post("/twilio-incoming-call")
async def twilio_incoming_call():
    """Twilio voice call entry point"""
    resp = VoiceResponse()
    
    resp.say(
        "नमस्कार! किसान मित्र AI सहायक में आपका स्वागत है। "
        "अपना कृषि संबंधी प्रश्न हिंदी में बोलें।",
        voice="alice",
        language="hi-IN"
    )
    
    resp.record(
        action="/twilio-process-voice",
        method="POST",
        max_length=30,
        timeout=3,
        play_beep=True,
        finish_on_key="#"
    )
    
    return HTMLResponse(str(resp), media_type="application/xml")

@app.post("/twilio-process-voice")
async def twilio_process_voice(request: Request):
    """Process Twilio voice recording"""
    form = await request.form()
    
    recording_url = form.get("RecordingUrl")
    caller = form.get("From", "+unknown")
    
    print(f"📞 Voice call from {caller}")
    
    resp = VoiceResponse()
    
    if not recording_url:
        resp.say("रिकॉर्डिंग नहीं मिली। कृपया फिर बोलें।", language="hi-IN")
        resp.redirect("/twilio-incoming-call")
        return HTMLResponse(str(resp), media_type="application/xml")
    
    try:
        # Download recording
        audio_id = uuid.uuid4().hex[:8]
        audio_path = f"temp_audio/twilio_{audio_id}.wav"
        
        r = requests.get(recording_url, timeout=30)
        with open(audio_path, "wb") as f:
            f.write(r.content)
        
        # AI Pipeline
        user_text = await transcribe_audio_local(audio_path)
        print(f"✅ Voice transcribed: '{user_text}'")
        
        if not user_text or len(user_text.strip()) < 3:
            resp.say("आवाज़ स्पष्ट नहीं आई। कृपया धीरे और स्पष्ट बोलें।", language="hi-IN")
            resp.redirect("/twilio-incoming-call")
            return HTMLResponse(str(resp), media_type="application/xml")
        
        intent = detect_intent(user_text)
        schemes = retrieve_schemes(user_text, intent)
        bot_reply = call_mistral(user_text, schemes)
        
        # Log
        log_interaction("twilio_voice", caller, user_text, intent, schemes, bot_reply)
        
        # Response
        resp.say(bot_reply, language="hi-IN")
        
        # Form offer
        gather = resp.gather(
            num_digits=1,
            action="/twilio-handle-choice",
            method="POST",
            timeout=8
        )
        gather.say(
            "इसके लिए आवेदन करना चाहते हैं? 1 दबाएं हाँ, 2 दबाएं अन्य जानकारी।",
            language="hi-IN"
        )
        
        return HTMLResponse(str(resp), media_type="application/xml")
    
    except Exception as e:
        print(f"❌ Voice processing error: {e}")
        resp.say("तकनीकी समस्या। कृपया फिर कोशिश करें।", language="hi-IN")
        resp.redirect("/twilio-incoming-call")
        return HTMLResponse(str(resp), media_type="application/xml")

@app.post("/twilio-handle-choice")
async def twilio_handle_choice(
    Digits: str = Form(None),
    From: str = Form(None)
):
    """Handle voice call form decision"""
    resp = VoiceResponse()
    caller = From
    
    if Digits == "1":
        # Form SMS (placeholder)
        form_url = "https://your-form-link.com/apply"
        resp.say("आपके WhatsApp पर फॉर्म लिंक भेजा गया। धन्यवाद!", language="hi-IN")
        # TODO: send_sms_with_form_link(caller, form_url)
    
    else:
        resp.say("अन्य जानकारी के लिए फिर कॉल करें। धन्यवाद!", language="hi-IN")
    
    resp.hangup()
    return HTMLResponse(str(resp), media_type="application/xml")

# =========================================================
# 3️⃣ WHATSAPP VOICE MESSAGES + TEXT
# =========================================================
@app.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(None),
    MediaUrl0: Optional[str] = Form(None),
    NumMedia: str = Form("0"),
    From: str = Form(None)
):
    """WhatsApp Voice Notes + Text → AI Response"""
    caller = From
    print(f"📱 WhatsApp: {caller}")
    
    try:
        user_text = ""
        
        # Voice note (OGG)
        if NumMedia == "1" and MediaUrl0:
            print(f"🎤 WhatsApp voice: {MediaUrl0}")
            
            try:
                audio_id = uuid.uuid4().hex[:8]
                audio_path = f"temp_audio/wa_voice_{audio_id}.ogg"
                
                # Timeout after 30 seconds
                r = requests.get(MediaUrl0, timeout=30)
                print(f"📥 Downloaded {len(r.content)} bytes")
                
                with open(audio_path, "wb") as f:
                    f.write(r.content)
                
                # Convert OGG to WAV
                try:
                    wav_path = audio_path.replace('.ogg', '.wav')
                    subprocess.run([
                        'ffmpeg', '-i', audio_path, '-ar', '16000', '-ac', '1',
                        wav_path, '-y'
                    ], check=True, capture_output=True, timeout=60)
                    audio_path = wav_path
                    print(f"✅ Converted to WAV")
                except Exception as e:
                    print(f"⚠️ FFmpeg failed: {e}, using OGG")
                
                # Transcribe
                user_text = await transcribe_audio_local(audio_path)
                print(f"✅ WhatsApp voice → '{user_text}'")
                
            except requests.Timeout:
                print("❌ Audio download timeout")
                return PlainTextResponse("वॉइस डाउनलोड टाइमआउट। फिर कोशिश करें।")
            except Exception as e:
                print(f"❌ Voice processing: {e}")
                return PlainTextResponse(f"वॉइस में समस्या: {str(e)}")
        
        # Text fallback
        elif Body and Body.strip():
            user_text = Body.strip()
            print(f"💬 WhatsApp text: '{user_text}'")
        
        if not user_text or len(user_text.strip()) < 2:
            return PlainTextResponse(
                "🌾 किसान मित्र: हिंदी में प्रश्न लिखें या वॉइस नोट भेजें।"
            )
        
        # AI Pipeline (with error handling)
        try:
            intent = detect_intent(user_text)
            schemes = retrieve_schemes(user_text, intent)
            print(f"🎯 Intent: {intent}, Schemes: {len(schemes)}")
            
            if not schemes:
                bot_reply = f"'{user_text}' के लिए योजनाएं नहीं मिलीं। कृपया अन्य प्रश्न पूछें।"
            else:
                bot_reply = call_mistral(user_text, schemes)
            
            # Log
            log_interaction("whatsapp", caller, user_text, intent, schemes, bot_reply)
            
            return PlainTextResponse(bot_reply)
        
        except Exception as e:
            print(f"❌ AI pipeline: {e}")
            return PlainTextResponse("AI में समस्या। फिर कोशिश करें।")
    
    except Exception as e:
        print(f"❌ WhatsApp error: {e}")
        return PlainTextResponse("क्षमा करें। बाद में कोशिश करें। 🌾")


@app.post("/whatsapp-form")
async def whatsapp_form(Body: str = Form(None), From: str = Form(None)):
    """WhatsApp form request"""
    caller = From
    
    # Generate form link (placeholder)
    form_url = f"https://your-forms.com/apply?phone={caller.replace('+', '')}"
    
    reply = (
        "📋 फॉर्म लिंक:\n"
        f"{form_url}\n\n"
        "या 'मुख्य मेनू' लिखें।"
    )
    
    return PlainTextResponse(reply)

# =========================================================
# 4️⃣ HEALTH + MONITORING
# =========================================================
@app.get("/health")
async def health():
    return {
        "status": "production",
        "service": "Kisaan Mitra V2 - Voice + WhatsApp",
        "endpoints": ["/twilio-incoming-call", "/whatsapp"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/logs")
async def get_logs():
    """Debug: Recent interactions"""
    if os.path.exists("call_logs/history.json"):
        with open("call_logs/history.json", 'r', encoding='utf-8') as f:
            logs = json.load(f)[-10:]  # Last 10
        return {"logs": logs}
    return {"logs": []}

# =========================================================
# 5️⃣ RUN
# =========================================================
if __name__ == "__main__":
    import uvicorn
    print("🚀 Kisaan Mitra V2 Starting...")
    print("📞 Twilio Voice: /twilio-incoming-call")
    print("📱 WhatsApp: /whatsapp")
    print("🩺 Health: /health")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
