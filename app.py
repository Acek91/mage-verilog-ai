import streamlit as st
import requests
import base64

# --- CONFIGURATION ---
# Fixed Model ID for February 2026
MODEL_ID = "gemini-3-pro-preview" 

st.set_page_config(page_title="MAGE AI: RTL & SV Hub", layout="wide")

def call_mage_ai(prompt, api_key, pdf_file=None):
    # Fixed endpoint using v1beta for PDF support
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={api_key}"
    
    parts = []
    
    # 1. Attach PDF if provided (Base64 Inline)
    if pdf_file is not None:
        try:
            pdf_bytes = pdf_file.read()
            pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            parts.append({
                "inline_data": {
                    "mime_type": "application/pdf",
                    "data": pdf_b64
                }
            })
        except Exception as e:
            st.error(f"File Error: {e}")

    # 2. Attach the Instruction/Requirement
    parts.append({"text": prompt})

    payload = {"contents": [{"parts": parts}]}
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=payload, headers=headers)
    res_json = response.json()
    
    if response.status_code != 200:
        error_msg = res_json.get('error', {}).get('message', 'Unknown Error')
        return f"🚨 API Error: {error_msg}"
    
    try:
        return res_json['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError):
        return "⚠️ Error: The AI returned an empty response. Check your input."

# --- TOOL INTERFACE ---
st.title("🛡️ MAGE AI: RTL, SV & Testbench Hub")
st.caption(f"Powered by {MODEL_ID} | No Installation Required")

with st.sidebar:
    st.header("🔑 Credentials")
    ai_key = st.text_input("Gemini API Key", type="password", help="Get from aistudio.google.com")
    
    st.divider()
    st.header("🎯 Mode Selection")
    mode = st.selectbox("What are we doing?", 
                        ["Design RTL Logic", "Generate Testbench", "Learn & Explain Concepts"])
    
    st.header("📚 Context (Optional)")
    uploaded_pdf = st.file_uploader("Upload Protocol Spec (PDF)", type="pdf")
    st.info("Upload a datasheet to make the AI follow specific industry rules.")

# Main Input
st.subheader("Enter your Requirements")
user_input = st.text_area("Example: '8-bit up/down counter with asynchronous reset' or 'Explain AXI4 handshaking'", 
                          height=150)

if st.button("Generate Result", type="primary"):
    if not ai_key:
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not user_input:
        st.warning("Please describe what you want to build or learn.")
    else:
        with st.spinner("Processing through Mage AI logic..."):
            # Custom Prompts based on Mode
            if mode == "Design RTL Logic":
                master_prompt = f"Act as a Senior RTL Design Engineer. Generate synthesizable Verilog/SystemVerilog code for: {user_input}. Ensure proper reset and clocking. Output ONLY code."
            elif mode == "Generate Testbench":
                master_prompt = f"Act as a Verification Engineer. Generate a complete SystemVerilog testbench for: {user_input}. Include clock generation, stimulus, and basic assertions. Output ONLY code."
            else:
                master_prompt = f"Act as a Digital Design Professor. Explain the following RTL concept clearly with examples: {user_input}."

            # Execute
            result = call_mage_ai(master_prompt, ai_key, uploaded_pdf)
            
            st.markdown("---")
            if "Error" in result:
                st.error(result)
            else:
                if mode != "Learn & Explain Concepts":
                    st.code(result, language="verilog")
                else:
                    st.markdown(result)
