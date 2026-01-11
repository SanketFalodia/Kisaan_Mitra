import streamlit as st
import asyncio
import os

from speech_to_text_free import transcribe_audio_local
from intent_detector import detect_intent
from multilingual_retriever import retrieve_schemes
from ollama_llm import call_mistral
from text_to_speech_free import synthesize_speech

st.set_page_config(page_title="Kisaan Mitra 🌾", layout="centered")

st.title("🌾 Kisaan Mitra – Voice AI Assistant")

os.makedirs("temp_audio", exist_ok=True)

uploaded_audio = st.file_uploader("🎤 किसान अपनी आवाज़ अपलोड करें", type=["wav", "mp3"])

user_text_input = st.text_input("✍️ या अपना प्रश्न लिखें")

if st.button("🔍 उत्तर प्राप्त करें"):
    with st.spinner("Processing..."):
        # 1️⃣ Get text
        if uploaded_audio:
            audio_path = f"temp_audio/{uploaded_audio.name}"
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.read())

            user_text = asyncio.run(transcribe_audio_local(audio_path))
        else:
            user_text = user_text_input

        if not user_text:
            st.error("❌ कोई इनपुट नहीं मिला")
            st.stop()

        st.success(f"👨‍🌾 किसान का प्रश्न: {user_text}")

        # 2️⃣ Intent
        intent = detect_intent(user_text)
        st.info(f"🎯 Detected Intent: {intent}")

        # 3️⃣ RAG
        schemes = retrieve_schemes(user_text, intent)

        # 4️⃣ LLM
        response = call_mistral(user_text, schemes)
        st.markdown("### 🤖 उत्तर")
        st.write(response)

        # 5️⃣ TTS
        audio_path = asyncio.run(synthesize_speech(response))
        st.audio(audio_path)
