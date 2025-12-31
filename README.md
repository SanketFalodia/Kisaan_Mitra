# 🌾 Kisaan Mitra

**Kisaan Mitra** is an **AI-powered, voice-first assistant** designed to help Indian farmers—especially from **Uttarakhand (Garhwal & Kumaoni regions)**—discover and understand **government agricultural schemes** in their **local languages**.

---

## 🚜 The Problem

- 🇮🇳 **70% of Indian farmers** speak Hindi or regional languages  
- 🌐 Most government scheme portals are **English-only**  
- 🧾 Finding eligible schemes requires navigating **complex forms**  
- 📱 **Limited digital literacy** among rural farmers  

---

## 💡 The Solution

A **voice-first, multilingual AI assistant** that:

- 🎙️ Listens to farmers in their **native language** (Hindi, Garhwali, Kumaoni)
- 🧠 Understands **farmer needs & disasters**
- 📚 Retrieves **eligible government schemes in real time**
- 🔊 Responds **naturally in the same language**

---

## ✨ Features

### 🎤 Voice-First Interface
- Local **Speech-to-Text** using **Whisper (MEDIUM model)**
- Hindi agricultural terminology understanding
- **Text-to-Speech** via **Edge-TTS**
- Offline TTS fallback support

---

### 🧠 Intelligent Intent Detection
- Detects farmer needs:
  - Crop loss  
  - Pest/disease  
  - Irrigation  
  - Soil fertility  
- Identifies disasters:
  - Flood  
  - Drought  
  - Hail  
  - Frost  
  - Cyclone  
- Extracts **farmer age** from speech
- Maps intents to **government scheme categories**

---

### 📚 RAG-Powered Scheme Matching
- **ChromaDB** for vector-based semantic search
- Intent + disaster → scheme eligibility mapping
- Age-based filtering
- Multilingual support:
  - Hindi  
  - English  
  - Garhwali  
  - Kumaoni  

---

### 🔒 Privacy-First Design
- 🔐 **100% local processing**
- 🚫 No cloud API calls for speech
- 🗃️ No data retention
- 🔓 Open-source models
- 📴 Zero external dependencies during inference

---

### 📱 Web & Future Integrations
- ✅ Streamlit web interface (current)
- ⚡ FastAPI backend (scalable)
- 📞 WhatsApp & IVR-ready (Round 2)

---

## 🏗️ Architecture

### 🔹 Current System (Round 1)

Farmer (Voice Input)
↓
Whisper MEDIUM (Speech-to-Text)
↓
Intent Detector (Keyword Matching)
↓
Multilingual Scheme Retriever (ChromaDB + Semantic Search)
↓
Scheme Filtering (Intent / Disaster / Age)
↓
LLM Response Generator (Ollama Mistral)
↓
Edge-TTS (Voice Output)
↓
Farmer (Voice Response)


---

## 📁 Project Structure

kisaan-mitra/
│
├── main_app.py # FastAPI backend (primary entry point)
├── streamlit_app.py # Streamlit web interface
├── requirements.txt # Python dependencies
├── uttarakhand_schemes.json # Government scheme database
│
├── audio_processor.py # Whisper + TTS wrappers
├── intent_detector.py # Hindi keyword-based intent extraction
│
├── rag/
│ └── multilingual_retriever.py # ChromaDB-based scheme retrieval
│
├── README.md # Project documentation



---

## 🚀 Round 2 Improvements (Planned)

### 🔌 1. WhatsApp & IVR Integration
- WhatsApp voice message support
- IVR phone gateway (Exotel / Twilio)
- Multi-turn conversations
- Message persistence

---

### 🌍 2. Language Expansion
- Fine-tuned Whisper models for Garhwali & Kumaoni
- Regional dialect handling
- Hinglish transliteration
- Multiple TTS voices (male/female, regional accents)

---

### 🔐 3. Security & Privacy
- On-device encryption
- User consent framework
- Data retention policies
- Audit logs

---

### 🗄️ 4. Real Government Portal Integration
- CAPTCHA-safe form filling
- Aadhaar-based auto-fill
- OCR-based document upload
- Application status tracking

---

### 📊 5. Advanced Features
- User history & preferences
- Personalized scheme recommendations
- Offline edge deployment
- Analytics dashboard

---

### 🎓 6. Accessibility
- Low-bandwidth support
- Hearing-impaired support (captions)
- Visually-impaired support (audio descriptions)
- Accessibility audit

---

## 🤝 Contribution

This is the work of team Neobots for Hack The Winter - The Second Wave (Angry Bird Edition)

---

