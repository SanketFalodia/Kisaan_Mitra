# Kisaan Mitra

Kisaan Mitra is an AI-powered voice assistant designed to help Indian farmers (especially those in Uttarakhand, Garhwal, and Kumaoni regions) discover government agricultural schemes using their local languages.

The Problem
70% of Indian farmers speak Hindi/regional languages

Most government scheme portals are English-only

Finding eligible schemes requires navigating complex forms

Limited digital literacy among rural farmers

The Solution
A voice-first, multilingual AI assistant that:

Listens to farmers in their native language (Hindi, Garhwali, Kumaoni)

Understands their needs and disasters

Retrieves eligible schemes in real-time

Responds naturally in their language
---

## Features

🎤 Voice-First Interface
Local speech-to-text (Whisper MEDIUM model)

Natural language understanding of Hindi agricultural terminology

Text-to-speech responses (Edge-TTS + offline fallback)

🧠 Intelligent Intent Detection
Detects farmer needs: crop loss, pest/disease, irrigation, soil fertility, etc.

Identifies disasters: flood, drought, hail, frost, cyclone

Extracts farmer age from speech

Maps intents to actual government scheme categories

📚 RAG-Powered Scheme Matching
ChromaDB vector search for semantic scheme retrieval

Intent/disaster mapping to scheme eligibility criteria

Age-based filtering

Multilingual support (Hindi, English, Garhwali, Kumaoni)

🔒 Privacy-First Design
100% local processing (no cloud API calls for speech)

No data retention

Open-source models

Zero external dependencies for inference

📱 Web & Future Integrations
Streamlit web interface (current)

FastAPI backend (scalable)

Ready for WhatsApp/IVR integration (Round 2) 

---

## Architecture

Current System (Round 1)

Farmer (Voice Input)
    ↓
Whisper MEDIUM (Speech-to-Text) [Local, Hindi support]
    ↓
Intent Detector (Keyword matching)
    ↓
MultilingualSchemeRetriever (ChromaDB + Semantic Search)
    ↓
Scheme Filtering (Intent/Disaster/Age matching)
    ↓
LLM Response Generation (Ollama Mistral)
    ↓
Edge-TTS (Text-to-Speech) [Natural voice output]
    ↓
Farmer (Voice Output)

---

## Project Structure

kisaan-mitra/
│
├── main_app.py                    # FastAPI backend (primary entry point)
├── streamlit_app.py               # Streamlit web interface
├── requirements.txt               # Python dependencies
├── uttarakhand_schemes.json       # Scheme database
│
├── audio_processor.py             # Whisper + TTS wrappers (MEDIUM model)
├── intent_detector.py             # Hindi keyword matching + intent extraction
│
├── rag/
│   └── multilingual_retriever.py  # ChromaDB-based scheme retrieval
│
│── README.md                  # This file




---

## Round 2 Improvements

🔌 1. WhatsApp & IVR Integration
WhatsApp API integration for voice messages

Phone gateway integration (Exotel, Twilio)

Multi-turn conversation support

Message persistence

🌍 2. Language Expansion
Fine-tuned Whisper models for Garhwali/Kumaoni

Regional dialect support

Transliteration (Hinglish input)

Multiple TTS voices (male/female, regional accents)

🔐 3. Security & Privacy
On-device encryption

User consent framework

Data retention policies

Audit logs

🗄️ 4. Real Portal Integration
CAPTCHA-safe form filling

Auto-fill Aadhaar-based data

Document upload (OCR-based)

Application status tracking

📊 5. Advanced Features
User history & preferences

Personalized recommendations

Offline mode (edge deployment)

Analytics dashboard

🎓 6. Accessibility
Low-bandwidth support

Hearing-impaired support (captions)

Visually-impaired support (audio descriptions)

Accessibility audit

