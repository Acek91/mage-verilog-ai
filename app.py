import streamlit as st
import requests
import json

# App Configuration
st.set_page_config(page_title="MAGE AI: Verilog Generator", layout="wide")

# Helper: Call Gemini AI
def call_gemini(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, headers=headers, json=data)
    try:
        return response.json()['candidates'][0]['content']['parts'][0]['text'].replace("```verilog", "").replace("```", "").strip()
    except:
        return "Error: Check your AI API Key."

# Helper: Call JDoodle Cloud Compiler (Zero Install Verilog Check)
def cloud_compile(code, client_id, client_secret):
    url = "https://api.jdoodle.com/v1/execute"
    payload = {
        "clientId": client_id, "clientSecret": client_secret,
        "script": code, "language": "verilog", "versionIndex": "0"
    }
    response = requests.post(url, json=payload)
    res = response.json()
    output = res.get("output", "")
    is_success = res.get("statusCode") == 200 and "error" not in output.lower()
    return is_success, output

# --- UI ---
st.title("🛡️ MAGE AI: RTL Agent")
st.markdown("Generate and verify Verilog protocols in the cloud—no installation required.")

with st.sidebar:
    st.header("🔑 API Credentials")
    ai_key = st.text_input("Gemini API Key", type="password")
    jd_id = st.text_input("JDoodle Client ID")
    jd_secret = st.text_input("JDoodle Client Secret", type="password")
    st.info("Get keys at: aistudio.google.com & jdoodle.com")

prompt = st.text_area("Requirement (e.g. AXI4-Lite Slave with 2 regs)", height=150)
protocol = st.selectbox("Protocol Standard", ["Generic", "AXI4-Lite", "SPI", "I2C", "UART"])

if st.button("Generate & Cloud-Verify", type="primary"):
    if not (ai_key and jd_id and jd_secret):
        st.error("Please provide all API keys in the sidebar.")
    else:
        with st.spinner("AI Generating..."):
            code = call_gemini(f"Write a {protocol} Verilog module: {prompt}. Only code.", ai_key)
            st.subheader("Generated RTL")
            st.code(code, language="verilog")
            
            with st.spinner("Cloud Compiler Checking..."):
                success, logs = cloud_compile(code, jd_id, jd_secret)
                if success:
                    st.success("✅ Syntax Verified!")
                else:
                    st.warning("⚠️ Syntax Errors Found")
                    st.text_area("Compiler Output", logs)
                    # Auto-fix attempt
                    if st.button("Auto-Fix Errors"):
                        fixed_code = call_gemini(f"Fix this Verilog code based on errors: {logs}\nCode:\n{code}", ai_key)
                        st.code(fixed_code, language="verilog")
