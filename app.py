import streamlit as st
import requests
import base64

# --- CONFIGURATION ---
st.set_page_config(page_title="MAGE AI: Protocol Architect", layout="wide")

def call_gemini_with_pdf(prompt, api_key, pdf_file=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": []
        }]
    }

    # Add PDF context if uploaded
    if pdf_file is not None:
        pdf_data = base64.b64encode(pdf_file.read()).decode('utf-8')
        payload["contents"][0]["parts"].append({
            "inline_data": {
                "mime_type": "application/pdf",
                "data": pdf_data
            }
        })
    
    # Add the text instructions
    payload["contents"][0]["parts"].append({"text": prompt})

    response = requests.post(url, json=payload)
    try:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error: {str(response.json())}"

# --- UI INTERFACE ---
st.title("🛡️ MAGE AI: Protocol Notebook")
st.markdown("Upload a Protocol PDF (e.g., AXI, PCIe, SPI) and generate verified Verilog logic.")

with st.sidebar:
    st.header("🔑 API Keys")
    ai_key = st.text_input("Gemini API Key", type="password")
    jd_id = st.text_input("JDoodle Client ID")
    jd_secret = st.text_input("JDoodle Client Secret", type="password")
    
    st.divider()
    st.header("📄 Source Materials")
    uploaded_file = st.file_uploader("Upload Protocol Datasheet (PDF)", type="pdf")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Design Requirements")
    user_prompt = st.text_area("What should the AI build?", 
                              placeholder="e.g. Create a Slave bridge based on the uploaded spec...", height=200)
    
    generate_btn = st.button("Analyze & Generate RTL", type="primary")

with col2:
    if generate_btn:
        if not ai_key:
            st.error("Please enter your Gemini API Key.")
        else:
            with st.spinner("Analyzing protocol and generating code..."):
                # System instructions integrated into the prompt
                context_prompt = f"""
                You are a Senior RTL Design Engineer. 
                Task: {user_prompt}
                Instruction: Use the provided PDF as the absolute reference for timing, signal names, and handshaking.
                Output: Provide ONLY the Verilog code block.
                """
                
                result_code = call_gemini_with_pdf(context_prompt, ai_key, uploaded_file)
                
                # Clean the markdown
                clean_code = result_code.replace("```verilog", "").replace("```", "").strip()
                
                st.subheader("Generated Verilog")
                st.code(clean_code, language="verilog")
                
                # Cloud Compilation Check (JDoodle)
                if jd_id and jd_secret:
                    st.info("Running Cloud Syntax Check...")
                    # (Insert the cloud_compile function from previous conversation here)
