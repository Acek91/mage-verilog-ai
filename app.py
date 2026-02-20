import streamlit as st
import requests
import base64
import socket
import time

# --- FEB 2026 STABILITY FIX: Force IPv4 to prevent socket hangs ---
_old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = _old_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

# --- CONFIGURATION ---
# Using the brand new Gemini 3.1 Pro (Released Feb 19, 2026)
MODEL_ID = "gemini-3.1-pro-preview" 

st.set_page_config(page_title="🛡️ MAGE AI: Universal RTL Hub", layout="wide")

# Professional Engineer Dark Theme
st.markdown("""
    <style>
    .main { background-color: #0b0d11; color: #e0e0e0; }
    .stCodeBlock { border: 1px solid #00ffcc; border-radius: 10px; }
    .stButton>button { width: 100%; background-color: #00ffcc !important; color: #000 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def call_mage_ai_with_retry(prompt, api_key, pdf_file=None, retries=2):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={api_key}"
    
    parts = []
    if pdf_file:
        pdf_b64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        parts.append({"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}})
    
    # Embedding strict hardware rules from our conversation
    full_prompt = f"Design Instructions: No 'inside' operator, use 'always_comb' and 'always_ff', logic types only.\n\n{prompt}"
    parts.append({"text": full_prompt})
    
    payload = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192}}

    for attempt in range(retries + 1):
        try:
            # High timeout (600s) for complex RTL reasoning
            response = requests.post(url, json=payload, timeout=(15, 600))
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except (requests.exceptions.RequestException, KeyError) as e:
            if attempt < retries:
                time.sleep(2) # Brief wait before retry
                continue
            return f"🚨 API Error: {str(e)}. Please check if your API key has Gemini 3.1 access."

# --- UI LAYOUT ---
st.title("🛡️ MAGE AI: Universal RTL & SV Hub")
st.caption(f"Currently using: {MODEL_ID} (High Reasoning Mode)")

with st.sidebar:
    st.header("🔑 Credentials")
    api_key = st.text_input("Gemini API Key", type="password")
    st.divider()
    hdl_lang = st.selectbox("Language", ["SystemVerilog", "Verilog", "VHDL", "Chisel", "BSV"])
    task = st.radio("Mode", ["Module Design", "Testbench Generation", "Concept Explanation"])
    uploaded_pdf = st.file_uploader("Upload Spec/Datasheet (Optional)", type="pdf")

user_input = st.text_area("Requirements:", height=200, placeholder="e.g., AXI4-Lite Slave Interface with 4 registers...")

if st.button("🚀 EXECUTE GENERATION"):
    if not api_key:
        st.error("Missing API Key.")
    else:
        with st.spinner("Mage AI is performing Deep Hardware Reasoning..."):
            prompt = f"Act as a Principal Hardware Engineer. Generate {hdl_lang} code for: {user_input}. Ensure syntax is 100% correct."
            result = call_mage_ai_with_retry(prompt, api_key, uploaded_pdf)
            
            st.markdown("### 🛠️ Hardware Output")
            if "```" in result:
                parts = result.split("```")
                st.info("Design Reasoning:\n" + parts[0])
                st.code(parts[1].replace("verilog", "").replace("vhdl", "").replace("systemverilog", ""), language="verilog")
            else:
                st.write(result)
