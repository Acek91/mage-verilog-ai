import streamlit as st
import requests
import base64

# --- CONFIGURATION ---
MODEL_ID = "gemini-2.5-flash" 

st.set_page_config(page_title="🛡️ MAGE AI: Universal RTL Architect", layout="wide")

def call_mage_ai(prompt, api_key, pdf_file=None):
    # Fixed endpoint for 2026
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={api_key}"
    parts = []
    
    if pdf_file:
        pdf_b64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        parts.append({"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}})
    
    parts.append({"text": prompt})
    payload = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.15}}
    
    try:
        # UPDATED: timeout=(connection_timeout, read_timeout)
        # 10s to connect, 300s to wait for the full RTL code generation
        response = requests.post(
            url, 
            json=payload, 
            headers={'Content-Type': 'application/json'},
            timeout=(10, 300) 
        )
        response.raise_for_status() # Check for HTTP errors
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except requests.exceptions.Timeout:
        return "🚨 Timeout Error: The AI took too long to generate the code. Try a simpler prompt or a smaller module."
    except Exception as e:
        return f"🚨 Error: {str(e)}"

# --- REST OF YOUR UI CODE REMAINS THE SAME ---
st.title("🛡️ MAGE AI: Universal RTL Architect")
# ... [rest of the Streamlit code provided previously]
