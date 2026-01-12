# 🌾 Kisaan Mitra – Round 2

Kisaan Mitra Round 2 is an enhanced, production‑ready evolution of the original Kisaan Mitra system. It focuses on **scalability, reliability, multilingual intelligence, and real‑world deployment readiness**, while continuing to prioritize **privacy‑first, voice‑first access** for Indian farmers.

## Demo

 **Watch the working demo here:**  
 (https://drive.google.com/file/d/1b9KcUoTV2QGk6u-SrlQ7KnevIFCybRK_/view?usp=sharing)


##  Vision (Round 2)

Enable farmers—especially from Uttarakhand’s **Garhwali and Kumaoni regions**—to **access government agricultural schemes effortlessly using voice**, across **web, IVR, and messaging platforms**, even in low‑connectivity environments.

Round 2 transforms Kisaan Mitra from a demo‑grade assistant into a **modular, extensible AI platform**.


### 1️ FastAPI‑Based Scalable Backend

* Production‑grade **FastAPI server**
* Async request handling for voice queries
* Modular service separation (STT, Intent, RAG, LLM, TTS)
* Health checks & API‑ready endpoints

---

### 2️ Improved Voice Pipeline

* **Local Whisper (CPU‑friendly)** for speech‑to‑text
* Noise‑robust transcription
* Better handling of Hindi agricultural terminology
* Structured audio upload & processing pipeline

---

### 3️ Stronger Intent & Disaster Detection

* Deterministic **keyword + rule‑based intent engine**
* Disaster identification:

  * Flood
  * Drought
  * Hailstorm
  * Frost
  * Cyclone
* Designed to work **without fine‑tuning or cloud LLMs**

---

### 4️ RAG 2.0 – Multilingual Scheme Retrieval

* **ChromaDB** vector store
* Semantic embeddings for scheme descriptions
* Retrieval based on:

  * Farmer intent
  * Disaster type
  * Age eligibility
  * Language preference
* Supports:

  * Hindi
  * English
  * Garhwali (text‑level)
  * Kumaoni (text‑level)

---

### 5️ Local LLM via Ollama

* **Ollama + Mistral** for response generation
* Zero cloud dependency
* Context‑aware responses using retrieved schemes
* Deterministic prompt templates

---

### 6️ Multilingual Voice Response (TTS)

* **Edge‑TTS** for natural speech output
* Language‑matched voice responses
* Offline‑fallback friendly design

---

### 7️ Privacy‑First Architecture

* 100% **local inference**
* No audio or text stored permanently
* No third‑party API calls during inference
* Farmer data never leaves the system

---

##  Architecture (Round 2)

<img width="1078" height="462" alt="image" src="https://github.com/user-attachments/assets/cb47238a-d2c1-48b1-8094-f953abf9af8b" />


---

## Project Structure (Round 2)

```
Kisaan_Mitra_R2/
│
├── main.py                     # FastAPI entry point
├── requirements.txt            # Dependencies
├── uttarakhand_schemes.json    # Scheme knowledge base
│
├── speech_to_text_free.py      # Whisper STT (local)
├── text_to_speech_free.py      # Edge‑TTS wrapper
├── intent_detector.py          # Intent & disaster detection
│
├── multilingual_retriever.py   # RAG using ChromaDB
├── ollama_llm.py               # Ollama‑Mistral interface
│
├── test_voice_query.py         # End‑to‑end pipeline test
└── README.md
```

---

##  How to Run (Developer Setup)

### 1️ Create Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 2️ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️ Start Ollama & Pull Model

```bash
ollama serve
ollama pull mistral
```

### 4️ Run Backend Server

```bash
python main.py
```

### 5️ Test Voice API

```bash
curl -X POST http://localhost:8000/voice-query -F "audio=@test.wav"
```



##  Design Philosophy

*  No cloud STT/TTS APIs
*  No fine‑tuning dependency
*  No farmer data retention
*  Deterministic logic where possible
*  Local‑first AI
*  Modular & replaceable components



##  Roadmap Beyond Round 2

###  WhatsApp & IVR Integration

* Voice notes as input
* Multi‑turn conversations
* Farmer call‑back system

###  Language Expansion

* Fine‑tuned Whisper for Garhwali & Kumaoni
* Hinglish transliteration support
* Multiple regional TTS voices

###  Government Portal Integration

* OCR‑based document handling
* Auto‑fill scheme applications
* Application status tracking

###  Accessibility

* Low‑bandwidth mode
* Audio‑only workflows
* Assisted navigation for elderly farmers

---

##  Outcome

Kisaan Mitra Round 2 demonstrates that **powerful AI systems for social good** can be:

* Local
* Private
* Affordable
* Language‑inclusive

— without relying on expensive cloud infrastructure.

