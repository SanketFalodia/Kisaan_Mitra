import streamlit as st
import requests
import json
import time
from pathlib import Path
import numpy as np
from datetime import datetime
import os
from typing import Optional, Dict, List

# Page Configuration

st.set_page_config(
    page_title="Kisaan Mitra - कृषि सहायता",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Kisaan Mitra - AI Assistant for Farmers"
    }
)

# Custom CSS Styling

st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #2ecc71;
            --secondary-color: #3498db;
            --danger-color: #e74c3c;
            --warning-color: #f39c12;
        }
        
        /* Custom styling */
        .main-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            border-radius: 10px;
            color: white;
            margin-bottom: 30px;
        }
        
        .scheme-card {
            background-color: #f8f9fa;
            border-left: 5px solid #2ecc71;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .language-badge {
            display: inline-block;
            padding: 5px 10px;
            background-color: #e8f5e9;
            border-radius: 20px;
            font-weight: bold;
            color: #2ecc71;
            margin: 5px 5px 5px 0;
        }
        
        .confidence-bar {
            background-color: #ecf0f1;
            border-radius: 10px;
            height: 8px;
            margin: 5px 0;
        }
        
        .info-box {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .success-box {
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        .error-box {
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)


# Session State Initialization


if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

if "last_query" not in st.session_state:
    st.session_state.last_query = None

if "last_response" not in st.session_state:
    st.session_state.last_response = None

if "query_history" not in st.session_state:
    st.session_state.query_history = []


# Helper Functions


def check_api_health(api_url: str) -> bool:
    """Check if API is running"""
    try:
        response = requests.get(f"{api_url}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def send_text_query(query: str, language: Optional[str] = None) -> Dict:
    """Send text query to API"""
    try:
        params = {"query": query}
        if language:
            params["language"] = language
        
        response = requests.post(
            f"{st.session_state.api_url}/text-query",
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Is it running?"}
    except Exception as e:
        return {"error": str(e)}

def send_audio_query(audio_file, language: Optional[str] = None) -> Dict:
    """Send audio file to API"""
    try:
        files = {"file": audio_file}
        params = {}
        if language:
            params["language"] = language
        
        response = requests.post(
            f"{st.session_state.api_url}/process-audio",
            files=files,
            params=params,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    
    except requests.exceptions.Timeout:
        return {"error": "Processing timed out. Please try again."}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Is it running?"}
    except Exception as e:
        return {"error": str(e)}

def fetch_all_schemes() -> List[Dict]:
    """Fetch all available schemes"""
    try:
        response = requests.get(
            f"{st.session_state.api_url}/schemes",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("schemes", [])
        else:
            return []
    except:
        return []

def fetch_scheme_details(scheme_id: str) -> Optional[Dict]:
    """Fetch detailed information about a scheme"""
    try:
        response = requests.get(
            f"{st.session_state.api_url}/scheme/{scheme_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def display_scheme_card(scheme: Dict):
    """Display a single scheme card"""
    with st.container():
        st.markdown(f"""
            <div class="scheme-card">
                <h4> {scheme.get('scheme_name', 'Unknown Scheme')}</h4>
                <p><b>Scheme ID:</b> {scheme.get('scheme_id', 'N/A')}</p>
                <p><b>Intent:</b> {scheme.get('intent', 'N/A').replace('_', ' ').title()}</p>
                <p><b>Required Fields:</b></p>
                <ul>
        """, unsafe_allow_html=True)
        
        required_fields = scheme.get('required_fields', [])
        if isinstance(required_fields, str):
            required_fields = required_fields.split(',')
        
        for field in required_fields[:5]:  # Show first 5 fields
            st.markdown(f"  - {field.strip().replace('_', ' ').title()}", unsafe_allow_html=True)
        
        if len(required_fields) > 5:
            st.markdown(f"  - ... and {len(required_fields) - 5} more fields", unsafe_allow_html=True)
        
        st.markdown(f"""
                </ul>
                <p><a href="{scheme.get('official_url', '#')}" target="_blank">
                    📖 View Official Details →
                </a></p>
            </div>
        """, unsafe_allow_html=True)

def get_language_emoji(language: str) -> str:
    """Get emoji for language"""
    language_map = {
        "hi": "🇮🇳",
        "en": "🇬🇧",
        "garhwali": "⛰️",
        "kumaoni": "🏔️"
    }
    return language_map.get(language, "🌐")

# Main App

def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1> किसान मित्र - Kisaan Mitra</h1>
            <h3>AI-Powered Agricultural Assistant</h3>
            <p>Get instant government scheme recommendations for your farm</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("Settings")
        
        # API Configuration
        st.subheader("API Configuration")
        st.session_state.api_url = st.text_input(
            "API URL",
            value=st.session_state.api_url,
            help="Enter the FastAPI server URL"
        )
        
        # Check API Health
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Check API"):
                if check_api_health(st.session_state.api_url):
                    st.success(" API is running!")
                else:
                    st.error(" API is not responding")
        
        with col2:
            if st.button(" Refresh"):
                st.rerun()
        
        st.divider()
        
        # Language Selection
        st.subheader("Language Preference")
        selected_language = st.selectbox(
            "Choose your language:",
            options=["hi", "garhwali", "kumaoni", "en"],
            format_func=lambda x: {
                "hi": "🇮🇳 हिंदी (Hindi)",
                "garhwali": "⛰️ गढ़वाली (Garhwali)",
                "kumaoni": "🏔️ कुमाऊनी (Kumaoni)",
                "en": "🇬🇧 English"
            }[x]
        )
        
        st.divider()
        
        # Quick Info
        st.subheader("About")
        st.info(
            """
            **Kisaan Mitra** helps farmers find relevant government schemes.
            
            • Ask about crop loss
            • Get scheme recommendations
            • Access official details
            
            Supports: Hindi, English, Garhwali, Kumaoni
            """
        )
        
        st.divider()
        
        # Query History
        if st.session_state.query_history:
            st.subheader(" Recent Queries")
            for i, query in enumerate(st.session_state.query_history[-5:], 1):
                st.caption(f"{i}. {query[:50]}...")
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Text Query", " Voice Query", "All Schemes", "FAQ"]
    )
    
   
    # TAB 1: 💬 TEXT QUERY
    
    with tab1:
        st.header("💬Text-Based Query")
        st.write("Ask your agricultural question in text format")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            user_query = st.text_area(
                "Enter your question:",
                placeholder="Example: मेरी फसल बाढ़ से खराब हो गई है। मेरी उम्र 45 साल है।",
                height=100
            )
        
        with col2:
            st.write("")
            st.write("")
            submit_button = st.button(" Submit Query", key="text_submit")
        
        if submit_button and user_query:
            with st.spinner("Processing your query..."):
                response = send_text_query(user_query, language=selected_language)
            
            if "error" in response:
                st.error(f" Error: {response['error']}")
            else:
                st.session_state.last_response = response
                st.session_state.last_query = user_query
                st.session_state.query_history.append(user_query)
                
                # Display Results
                st.success(" Query processed successfully!")
                
                # Detected Information
                st.subheader(" Detected Information")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Language",
                        f"{get_language_emoji(response.get('detected_language', 'unknown'))} " +
                        response.get('detected_language', 'Unknown').upper()
                    )
                
                with col2:
                    st.metric(
                        "Intent",
                        response.get('detected_intent', 'Unknown').replace('_', ' ').title()
                    )
                
                with col3:
                    st.metric(
                        "Disaster Type",
                        response.get('detected_disaster', 'Unknown').replace('_', ' ').title()
                    )
                
                with col4:
                    confidence = response.get('confidence', 0)
                    st.metric(
                        "Confidence",
                        f"{confidence*100:.0f}%"
                    )
                
                # Response Text
                st.subheader(" Response")
                st.info(response.get('text_response', 'No response generated'))
                
                # Eligible Schemes
                schemes = response.get('eligible_schemes', [])
                if schemes:
                    st.subheader(f" Eligible Schemes ({len(schemes)})")
                    for scheme in schemes:
                        display_scheme_card(scheme)
                else:
                    st.warning("No eligible schemes found for your criteria")
        
        elif submit_button:
            st.warning("Please enter a question first")
    
   
    # TAB 2: 🎤VOICE QUERY
   
    with tab2:
        st.header(" 🎤Voice-Based Query")
        st.write("Upload an audio file or record your question")
        
        audio_mode = st.radio(
            "Choose input method:",
            ["Upload Audio File", "Record Audio"]
        )
        
        audio_file = None
        
        if audio_mode == "Upload Audio File":
            audio_file = st.file_uploader(
                "Upload audio file (WAV, MP3, etc.)",
                type=["wav", "mp3", "m4a", "flac"]
            )
        else:
            audio_file = st.audio_input("Click to record (max 30 seconds)")
        
        if st.button(" Process Audio", key="audio_submit"):
            if audio_file:
                with st.spinner("Processing audio..."):
                    response = send_audio_query(audio_file, language=selected_language)
                
                if "error" in response:
                    st.error(f" Error: {response['error']}")
                else:
                    st.session_state.last_response = response
                    
                    # Display Results
                    st.success("Audio processed successfully!")
                    
                    # Detected Information
                    st.subheader(" Detected Information")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Transcribed Language", response.get('detected_language', 'Unknown').upper())
                    with col2:
                        st.metric("Intent", response.get('detected_intent', 'Unknown').replace('_', ' ').title())
                    with col3:
                        st.metric("Disaster", response.get('detected_disaster', 'Unknown').replace('_', ' ').title())
                    with col4:
                        st.metric("Confidence", f"{response.get('confidence', 0)*100:.0f}%")
                    
                    # Response Text
                    st.subheader(" AI Response")
                    st.info(response.get('text_response', 'No response generated'))
                    
                    # Response Audio (if available)
                    if response.get('audio_response_path'):
                        st.subheader(" Voice Response")
                        try:
                            with open(response['audio_response_path'], 'rb') as audio:
                                st.audio(audio.read(), format="audio/wav")
                        except:
                            st.warning("Could not load audio response")
                    
                    # Eligible Schemes
                    schemes = response.get('eligible_schemes', [])
                    if schemes:
                        st.subheader(f" Eligible Schemes ({len(schemes)})")
                        for scheme in schemes:
                            display_scheme_card(scheme)
                    else:
                        st.warning("No eligible schemes found for your criteria")
            else:
                st.warning("Please upload or record audio first")
    
  
    # TAB 3: ALL SCHEMES

    with tab3:
        st.header(" All Available Schemes")
        st.write("Browse all government schemes available in Uttarakhand")
        
        if st.button(" Load All Schemes"):
            with st.spinner("Loading schemes..."):
                schemes = fetch_all_schemes()
            
            if schemes:
                st.success(f" Loaded {len(schemes)} schemes")
                
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    search_term = st.text_input("Search schemes...")
                with col2:
                    intent_filter = st.selectbox(
                        "Filter by intent:",
                        ["All"] + list(set([s.get('intent', 'unknown') for s in schemes]))
                    )
                
                # Filter schemes
                filtered_schemes = schemes
                if search_term:
                    filtered_schemes = [
                        s for s in filtered_schemes
                        if search_term.lower() in s.get('scheme_name', '').lower()
                    ]
                if intent_filter != "All":
                    filtered_schemes = [
                        s for s in filtered_schemes
                        if s.get('intent') == intent_filter
                    ]
                
                st.info(f"Showing {len(filtered_schemes)} schemes")
                
                # Display schemes
                for scheme in filtered_schemes:
                    display_scheme_card(scheme)
            else:
                st.error("Could not load schemes")
    
    
    # TAB 4: ❓FAQ
   
    with tab4:
        st.header("❓ Frequently Asked Questions")
        
        faqs = [
            {
                "q": "किसान मित्र क्या है? (What is Kisaan Mitra?)",
                "a": "Kisaan Mitra is an AI-powered assistant that helps farmers find government agricultural schemes based on their situation, age, and disaster type."
            },
            {
                "q": "कौन से भाषाओं में समर्थन है? (Which languages are supported?)",
                "a": "We support Hindi, English, Garhwali, and Kumaoni languages for both voice and text input."
            },
            {
                "q": "मुझे कौन सी जानकारी देनी होगी? (What information do I need to provide?)",
                "a": "You need to tell us about: (1) Your age, (2) Type of disaster/crisis, (3) Type of agricultural support needed. Personal details are not stored."
            },
            {
                "q": "क्या मेरा डेटा सुरक्षित है? (Is my data safe?)",
                "a": "Yes! All processing happens locally. Your data is never sent to external servers. We don't store any personal information."
            },
            {
                "q": "आवेदन कैसे करें? (How do I apply?)",
                "a": "After finding a scheme, you'll get the official URL and list of required documents. You can apply directly through the government portal."
            },
            {
                "q": "क्या यह मुफ्त है? (Is this free?)",
                "a": "Yes! Kisaan Mitra is completely free. No charges for queries, recommendations, or service."
            }
        ]
        
        for i, faq in enumerate(faqs, 1):
            with st.expander(f"**{i}. {faq['q']}**"):
                st.write(faq['a'])
        
        # Contact Information
        st.divider()
        st.subheader(" Need Help?")
        st.info(
            """
            **For technical support:** github.com/kisaan-mitra
            
            **For scheme information:** Visit MyScheme.gov.in
            
            **Local agriculture office:** Contact your district agriculture department
            """
        )

if __name__ == "__main__":

    main()


