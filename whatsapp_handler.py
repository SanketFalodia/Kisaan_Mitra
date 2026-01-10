import os
import uuid
import tempfile
import httpx
from fastapi import APIRouter, Request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from audio_processor import MultilingualAudioProcessor
from intent_detector import IntentDetector
from multilingual_retriever import MultilingualSchemeRetriever
from main_app import _generate_response

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

router = APIRouter()
audio_processor = MultilingualAudioProcessor()
intent_detector = IntentDetector()
retriever = MultilingualSchemeRetriever()


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    Receives WhatsApp voice note from Twilio
    """
    form = await request.form()
    media_url = form.get("MediaUrl0")
    sender = form.get("From")

    resp = MessagingResponse()

    if not media_url:
        resp.message("कृपया अपनी समस्या आवाज़ में बताएं।")
        return str(resp)

    # Download audio from Twilio
    audio_path = os.path.join(
        tempfile.gettempdir(),
        f"wa_{uuid.uuid4()}.ogg"
    )

    async with httpx.AsyncClient() as client:
        r = await client.get(
            media_url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        )
        with open(audio_path, "wb") as f:
            f.write(r.content)

    # Speech to Text
    text, lang, conf = await audio_processor.speech_to_text(audio_path)

    if not text:
        resp.message("माफ़ कीजिए, आवाज़ साफ़ नहीं आई। कृपया दोबारा बोलें।")
        return str(resp)

    # Intent detection
    parsed = intent_detector.parse_query(text)

    # Scheme retrieval
    schemes = retriever.get_eligible_schemes(
        intent=parsed["intent"],
        disaster=parsed["disaster"],
        age=parsed["age"] if parsed["age"] > 0 else 30,
        language=lang
    )

    # Generate response text
    response_text = _generate_response(
        intent=parsed["intent"],
        disaster=parsed["disaster"],
        age=parsed["age"],
        eligible_schemes=schemes,
        language=lang
    )

    # Text → Speech (Edge-TTS)
    reply_audio = os.path.join(
        tempfile.gettempdir(),
        f"reply_{uuid.uuid4()}.wav"
    )

    audio_processor.text_to_speech_edge(
        response_text,
        language=lang,
        output_path=reply_audio
    )

    # Send voice reply
    twilio_client.messages.create(
        from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
        to=sender,
        media_url=f"{request.base_url}static/{os.path.basename(reply_audio)}"
    )

    return str(resp)
