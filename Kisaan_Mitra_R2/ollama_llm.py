

# ollama_llm.py
import subprocess

def call_mistral(text: str) -> str:
    """
    Call Ollama Mistral locally via CLI (UTF-8 safe, Windows compatible)
    """

    if not text or not text.strip():
        return "Sorry, I could not understand."

    try:
        # Run Ollama with UTF-8 safe input
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=text,
            capture_output=True,
            text=True,
            encoding="utf-8",   # 🔑 Fix Unicode (Hindi)
            errors="ignore",
            check=True
        )

        response = result.stdout.strip()

        if not response:
            return "Sorry, I could not generate a response."

        return response

    except subprocess.CalledProcessError as e:
        print("❌ Ollama runtime error:", e.stderr)
        return "Sorry, there was an error running the model."

    except FileNotFoundError:
        return "Ollama is not installed or not in PATH."

    except Exception as e:
        print("❌ Unexpected Ollama error:", e)
        return "Sorry, I could not process your request."

# ollama_llm.py

import subprocess

def call_mistral(user_query: str, schemes: list) -> str:
    context = ""
    for s in schemes:
        context += f"""
योजना: {s.get('name')}
विवरण: {s.get('description')}
पात्रता: {s.get('eligibility')}
लाभ: {s.get('benefits')}
\n
"""

    prompt = f"""
आप एक भारतीय कृषि सहायक AI हैं।
केवल नीचे दी गई सरकारी योजनाओं की जानकारी के आधार पर उत्तर दें।

{context}

किसान का प्रश्न:
{user_query}

सरल हिंदी में उत्तर दें।
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return result.stdout.strip()

    except Exception as e:
        print("❌ Ollama error:", e)
        return "माफ़ कीजिए, अभी उत्तर नहीं दे पा रहा हूँ।"


