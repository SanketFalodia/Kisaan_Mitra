from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import os
import uuid
import io
from datetime import datetime
import tempfile

# Import custom modules
from multilingual_retriever import MultilingualSchemeRetriever
from intent_detector import IntentDetector
from audio_processor import MultilingualAudioProcessor, MultilingualTranslator


# Initialize Components

app = FastAPI(
    title="Kisaan Mitra - Voice-First AI Assistant",
    description="AI-powered voice assistant for Indian farmers",
    version="1.0.0"
)

# Initialize services
retriever = MultilingualSchemeRetriever()
intent_detector = IntentDetector(model_name="mistral")
audio_processor = MultilingualAudioProcessor(model_size="base")
translator = MultilingualTranslator()


# Data Models


class FarmerQuery(BaseModel):
    """Structured query from farmer"""
    intent: str
    disaster: str
    age: int
    language: str = "hi"
    state: str = "Uttarakhand"

class AudioRequest(BaseModel):
    """Audio file processing request"""
    language: Optional[str] = None

class SchemeResponse(BaseModel):
    """Response with recommended schemes"""
    scheme_id: str
    scheme_name: str
    intent: str
    required_fields: List[str]
    official_url: str
    age_eligibility: str

class AssistantResponse(BaseModel):
    """Complete assistant response"""
    detected_language: str
    detected_intent: str
    detected_disaster: str
    farmer_age: int
    confidence: float
    eligible_schemes: List[SchemeResponse]
    text_response: str
    audio_response_path: Optional[str] = None


# Health Check Endpoint

@app.get("/health")
async def health_check():
    """Check if all services are running"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "llm": "initialized",
            "rag": "initialized",
            "audio": "initialized"
        }
    }


# Core Processing Endpoints

@app.post("/process-audio")
async def process_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Process audio file from farmer
    FIXED: Handles Streamlit audio input and file uploads
    
    Flow:
    1. Speech → Text (Whisper)
    2. Detect Intent & Language
    3. Retrieve Eligible Schemes (RAG)
    4. Generate Response (LLM)
    5. Text → Speech
    
    Returns: Complete assistant response with audio
    """
    
    try:
        # FIX: Handle case where file doesn't have content_type
        # (Streamlit audio_input sends raw bytes, not UploadFile with content_type)
        if file is None:
            raise HTTPException(status_code=400, detail="No audio file received")
        
        # Check content type only if it exists
        if hasattr(file, 'content_type') and file.content_type:
            if not file.content_type.startswith("audio/"):
                raise HTTPException(status_code=400, detail="File must be audio")
        
        # Read audio file
        audio_data = await file.read()
        if not audio_data or len(audio_data) < 100:
            raise HTTPException(status_code=400, detail="Audio file is empty or too small")
        
        # Save to temporary file for processing
        temp_audio_path = os.path.join(tempfile.gettempdir(), f"audio_{uuid.uuid4()}.wav")
        
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)
        
        print(f" Saved audio to: {temp_audio_path}")
        print(f" Audio size: {len(audio_data)} bytes")
        
        # Step 1: Convert speech to text
        print(" Step 1: Converting speech to text")
        try:
            text, detected_language, stt_confidence = await audio_processor.speech_to_text(
                temp_audio_path,
                language=language
            )
        except Exception as e:
            print(f"STT Error: {e}")
            raise HTTPException(status_code=400, detail=f"Could not transcribe audio: {str(e)}")
        
        if not text or text.strip() == "":
            raise HTTPException(status_code=400, detail="Could not transcribe audio - please speak clearly")
        
        print(f" Transcribed text: {text}")
        print(f" Detected language: {detected_language}")
        print(f" STT Confidence: {stt_confidence:.2%}")
        
        # Step 2: Parse query and detect intent
        print(" Step 2: Detecting intent...")
        parsed_query = intent_detector.parse_query(text)
        
        intent = parsed_query["intent"]
        disaster = parsed_query["disaster"]
        age = parsed_query["age"]
        
        print(f" Intent: {intent}, Disaster: {disaster}, Age: {age}")
        
        # Step 3: Retrieve eligible schemes from RAG
        print(" Step 3: Retrieving eligible schemes")
        eligible_schemes = retriever.get_eligible_schemes(
            intent=intent,
            disaster=disaster,
            age=age if age > 0 else 30,  # Default age if not detected
            language=detected_language
        )
        
        print(f" Found {len(eligible_schemes)} eligible schemes")
        
        # Step 4: Generate text response
        print(" Step 4: Generating response")
        response_text = _generate_response(
            intent=intent,
            disaster=disaster,
            age=age,
            eligible_schemes=eligible_schemes,
            language=detected_language
        )
        
        # Step 5: Convert response to speech
        print(" Step 5: Converting response to speech...")
        output_audio_path = os.path.join(tempfile.gettempdir(), f"response_{uuid.uuid4()}.wav")
        
        try:
            tts_success = audio_processor.text_to_speech_edge(
                response_text,
                language=detected_language,
                output_path=output_audio_path
            )
            
            if not tts_success:
                print(" TTS failed, trying offline mode...")
                tts_success = audio_processor.text_to_speech_offline(
                    response_text,
                    output_path=output_audio_path
                )
            
            if not tts_success:
                output_audio_path = None
                print(" TTS unavailable, returning text only")
        except Exception as e:
            print(f"TTS Error: {e}")
            output_audio_path = None
        
        # Clean up temp audio file
        background_tasks.add_task(_safe_delete, temp_audio_path)
        
        # Prepare response
        response = AssistantResponse(
            detected_language=detected_language,
            detected_intent=intent,
            detected_disaster=disaster,
            farmer_age=age,
            confidence=parsed_query["confidence"],
            eligible_schemes=[
                SchemeResponse(
                    scheme_id=scheme["scheme_id"],
                    scheme_name=scheme["scheme_name"],
                    intent=scheme["intent"],
                    required_fields=scheme["required_fields"],
                    official_url=scheme["official_url"],
                    age_eligibility=scheme.get("age_eligibility", "")
                )
                for scheme in eligible_schemes
            ],
            text_response=response_text,
            audio_response_path=output_audio_path
        )
        
        print("Audio processing complete!")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        print(f" Error processing audio: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/text-query")
async def process_text_query(query: str, language: Optional[str] = None):
    """
    Process text query directly (for testing or text-based interactions)
    """
    try:
        if not query or query.strip() == "":
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Parse query
        parsed_query = intent_detector.parse_query(query)
        
        intent = parsed_query["intent"]
        disaster = parsed_query["disaster"]
        age = parsed_query["age"]
        detected_language = parsed_query["language"]
        
        # Retrieve schemes
        eligible_schemes = retriever.get_eligible_schemes(
            intent=intent,
            disaster=disaster,
            age=age if age > 0 else 30,
            language=detected_language
        )
        
        # Generate response
        response_text = _generate_response(
            intent=intent,
            disaster=disaster,
            age=age,
            eligible_schemes=eligible_schemes,
            language=detected_language
        )
        
        return {
            "detected_language": detected_language,
            "detected_intent": intent,
            "detected_disaster": disaster,
            "farmer_age": age,
            "confidence": parsed_query["confidence"],
            "eligible_schemes": eligible_schemes,
            "response_text": response_text
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schemes")
async def list_all_schemes(
    intent: Optional[str] = None,
    disaster: Optional[str] = None,
    age: Optional[int] = None
):
    """
    List available schemes with optional filtering
    """
    try:
        if intent and disaster and age:
            schemes = retriever.get_eligible_schemes(
                intent=intent,
                disaster=disaster,
                age=age
            )
        else:
            # Return all schemes
            all_results = retriever.collection.get()
            schemes = []
            for meta in all_results["metadatas"]:
                schemes.append({
                    "scheme_id": meta["scheme_id"],
                    "scheme_name": meta["scheme_name"],
                    "intent": meta["intent"],
                    "official_url": meta["official_url"]
                })
        
        return {
            "total_schemes": len(schemes),
            "schemes": schemes
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scheme/{scheme_id}")
async def get_scheme_details(scheme_id: str):
    """Get detailed information about a specific scheme"""
    try:
        details = retriever.get_scheme_details(scheme_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Scheme not found")
        
        return details
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Helper Functions

def _safe_delete(file_path: str):
    """Safely delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f" Deleted temp file: {file_path}")
    except Exception as e:
        print(f" Could not delete {file_path}: {e}")

def _generate_response(
    intent: str,
    disaster: str,
    age: int,
    eligible_schemes: List,
    language: str = "hi"
) -> str:
    """
    Generate farmer-friendly response text
    """
    
    # Greeting messages
    greetings = {
        "hi": "नमस्कार भाई! मैं आपके कृषि सहायता के लिए यहाँ हूँ।",
        "en": "Hello farmer! I'm here to help you with agricultural support.",
        "garhwali": "नमस्कार भैया! मैं तेरो कृषि सहायता के लिए यहाँ छु।",
        "kumaoni": "नमस्कार भैया! मैं तेरो खेतिहर सहायता के लिए यहाँ छु।"
    }
    
    # Build response
    response = greetings.get(language, greetings["hi"]) + "\n\n"
    
    if eligible_schemes:
        response += f"आपके लिए {len(eligible_schemes)} योजनाएं उपलब्ध हैं:\n\n"
        
        for i, scheme in enumerate(eligible_schemes, 1):
            response += f"{i}. {scheme['scheme_name']}\n"
            response += f"   आवश्यक दस्तावेज: {', '.join(scheme['required_fields'][:3])}\n"
            response += f"   अधिक जानकारी: {scheme['official_url']}\n\n"
    else:
        response += "क्षमा करें, आपकी स्थिति के लिए अभी कोई योजना उपलब्ध नहीं है।"
    
    return response


# Root Endpoint


@app.get("/")
async def root():
    """API documentation"""
    return {
        "name": "Kisaan Mitra - Voice-First AI Assistant",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process_audio": "POST /process-audio (multipart/form-data with audio file)",
            "text_query": "POST /text-query (with query parameter)",
            "list_schemes": "GET /schemes",
            "scheme_details": "GET /scheme/{scheme_id}",
            "docs": "/docs"
        }
    }


# Run Application

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False

    )
