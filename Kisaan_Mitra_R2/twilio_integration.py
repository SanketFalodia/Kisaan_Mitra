from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def create_ivr_response(message: str, gather_input: bool = False):
    """
    Create Twilio IVR response with optional DTMF input
    gather_input=True: Wait for user input (1 for yes, 2 for no)
    """
    response = VoiceResponse()
    response.say(message, voice='alice', language='hi-IN')
    
    if gather_input:
        gather = response.gather(
            num_digits=1,
            action='/handle-user-choice',
            method='POST',
            timeout=5
        )
        gather.say("कृपया 1 दबाएं हाँ के लिए, या 2 दबाएं नहीं के लिए", voice='alice', language='hi-IN')
    
    return str(response)

def send_sms_with_form_link(phone_number: str, scheme_name: str, form_url: str):
    """
    Send SMS with pre-filled form link to farmer
    """
    message_text = f"नमस्कार! {scheme_name} के लिए फॉर्म भरने के लिए यहाँ क्लिक करें: {form_url}"
    
    try:
        message = twilio_client.messages.create(
            body=message_text,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"✅ SMS sent to {phone_number}: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ SMS error: {e}")
        return False

def record_call_log(phone_number: str, user_query: str, schemes_offered: list, user_choice: str):
    """
    Log call details for analytics
    """
    log_entry = {
        "phone": phone_number,
        "query": user_query,
        "schemes": schemes_offered,
        "user_choice": user_choice,  # "yes", "no", "skip"
        "timestamp": str(__import__('datetime').datetime.now())
    }
    # TODO: Store in database
    print(f"📋 Call log: {log_entry}")
    return log_entry