from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from speech_to_text_free import transcribe_audio_local
from text_to_speech_free import synthesize_speech
from ollama_llm import call_mistral
from intent_detector import detect_intent
from multilingual_retriever import retrieve_schemes
from twilio_integration import create_ivr_response, send_sms_with_form_link, record_call_log
import os
import shutil
from twilio.twiml.voice_response import VoiceResponse

app = FastAPI(title="Voice-first AI Assistant - Kisaan Mitra")
os.makedirs("temp_audio", exist_ok=True)
os.makedirs("call_logs", exist_ok=True)

# ==================== ORIGINAL ENDPOINTS (UNCHANGED) ====================

@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    """Original endpoint - unchanged"""
    audio_path = f"temp_audio/{audio.filename}"
    with open(audio_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)
    
    user_text = await transcribe_audio_local(audio_path)
    if not user_text:
        return {"error": "Failed to transcribe audio."}
    
    bot_text = call_mistral(user_text)
    audio_out = await synthesize_speech(bot_text)
    if not audio_out:
        return {"error": "Failed to generate speech."}
    
    return {
        "user_text": user_text,
        "bot_text": bot_text,
        "audio_path": audio_out
    }

# ==================== NEW TWILIO ENDPOINTS ====================

@app.post("/twilio-incoming-call")
async def twilio_incoming_call(request: Request):
    """
    Twilio webhook for incoming calls
    Greet farmer and ask them to start speaking
    """
    response = VoiceResponse()
    response.say(
        "नमस्कार! किसान मित्र में आपका स्वागत है। कृपया अपना प्रश्न बताएं।",
        voice='alice',
        language='hi-IN'
    )
    
    # Record farmer's voice
    response.record(
        max_speech_time=30,
        action='/twilio-process-voice',
        method='POST',
        speech_timeout=2
    )
    
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.post("/twilio-process-voice")
async def twilio_process_voice(request: Request):
    """
    Process recorded voice from Twilio
    - Get audio URL
    - Transcribe with Whisper
    - Detect intent
    - Retrieve schemes
    - Generate response
    - Ask about form
    """
    form_data = await request.form()
    recording_url = form_data.get('RecordingUrl')
    call_sid = form_data.get('CallSid')
    from_number = form_data.get('From')
    
    print(f"📞 Call SID: {call_sid}, From: {from_number}, Recording: {recording_url}")
    
    # Download and transcribe audio
    import requests
    try:
        audio_response = requests.get(recording_url)
        audio_path = f"temp_audio/twilio_{call_sid}.wav"
        with open(audio_path, 'wb') as f:
            f.write(audio_response.content)
        
        # Transcribe with Whisper (UNCHANGED)
        user_text = await transcribe_audio_local(audio_path)
        if not user_text:
            return create_ivr_response("खेद है, आपके प्रश्न को समझ नहीं सके। कृपया फिर से कोशिश करें।")
        
        # Detect intent (UNCHANGED)
        intent = detect_intent(user_text)
        
        # Retrieve schemes (UNCHANGED)
        schemes = retrieve_schemes(user_text, intent)
        
        if not schemes:
            return create_ivr_response("खेद है, इस समय कोई उपयुक्त योजना नहीं मिली।")
        
        # Generate LLM response (UNCHANGED)
        llm_response = call_mistral(user_text, schemes)
        
        # Log the interaction
        scheme_names = [s.get('scheme_name', 'Unknown') for s in schemes]
        record_call_log(from_number, user_text, scheme_names, "pending")
        
        # Create Twilio response with scheme info + form offer
        response = VoiceResponse()
        response.say(llm_response, voice='alice', language='hi-IN')
        response.say(
            f"क्या आप {schemes[0].get('scheme_name', 'इस योजना')} के लिए फॉर्म भरना चाहते हैं?",
            voice='alice',
            language='hi-IN'
        )
        
        # Gather user choice (1=yes, 2=no)
        gather = response.gather(
            num_digits=1,
            action='/twilio-handle-choice',
            method='POST',
            timeout=5
        )
        gather.say(
            "1 दबाएं हाँ के लिए, 2 दबाएं नहीं के लिए",
            voice='alice',
            language='hi-IN'
        )
        
        return HTMLResponse(content=str(response), media_type="application/xml")
    
    except Exception as e:
        print(f"❌ Error processing voice: {e}")
        return create_ivr_response(f"त्रुटि: {str(e)}")

@app.post("/twilio-handle-choice")
async def twilio_handle_choice(request: Request):
    """
    Handle user's DTMF choice (1=yes, 2=no)
    Send form link via SMS or offer other schemes
    """
    form_data = await request.form()
    digits = form_data.get('Digits')
    from_number = form_data.get('From')
    
    response = VoiceResponse()
    
    if digits == '1':  # User wants form
        # TODO: Generate form URL with phone number pre-filled
        form_url = f"https://yourapp.com/form?phone={from_number}"
        
        response.say(
            "आपके फोन पर एक एसएमएस भेजा जा रहा है जिसमें फॉर्म की लिंक है।",
            voice='alice',
            language='hi-IN'
        )
        
        # Send SMS with form link
        # send_sms_with_form_link(from_number, scheme_name, form_url)
        
        response.hangup()
    
    elif digits == '2':  # User doesn't want form
        response.say(
            "ठीक है। आप किसी अन्य योजना के बारे में जानना चाहते हैं?",
            voice='alice',
            language='hi-IN'
        )
        response.gather(
            num_digits=1,
            action='/twilio-incoming-call',
            method='POST',
            timeout=5
        ).say("1 दबाएं हाँ के लिए, 2 दबाएं नहीं के लिए")
        response.hangup()
    
    else:
        response.say("खेद है, समझ नहीं आया। कृपया फिर से कोशिश करें।")
        response.redirect('/twilio-incoming-call')
    
    return HTMLResponse(content=str(response), media_type="application/xml")

# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Kisaan Mitra - Twilio Integration"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)