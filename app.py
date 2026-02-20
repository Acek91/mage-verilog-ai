import streamlit as st
import requests
import json
import base64

# --- PROFESSIONAL CONFIGURATION ---
# Gemini 2.5 Flash is the fastest & has the highest free quota in 2026
MODEL_ID = "gemini-2.5-flash" 

st.set_page_config(page_title="RTL ARCHITECT PRO", page_icon="🛡️", layout="wide")

# Custom Genuine CSS for a "Premium" look
st.markdown("""
    <style>
    .stTextArea textarea { font-family: 'Courier New', Courier, monospace; }
    .stCodeBlock { border-radius: 10px; border: 1px solid #4A90E2; }
    .main { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- RTL SYSTEM PROMPTS (Integrated from your snippet) ---
SYSTEM_PROMPT = "You are an expert in RTL design. You write SystemVerilog with no syntax errors and correct functionality."

EXTRA_RULES = """
Other requirements:
1. Don't use state_t; use localparam, reg, or logic.
2. Declare all ports and signals as logic.
3. Initialize signals without reset to a known value using 'initial' blocks.
4. Use always @(*) for combinational logic.
5. NEVER USE 'inside', 'unique', or 'unique0' keywords.
"""

def call_gemini_api(prompt, api_key, pdf_file=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={api_key}"
    
    parts = []
    if pdf_file:
        pdf_b64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        parts.append({"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}})
    
    parts.append({"text": f"{SYSTEM_PROMPT}\n\n{prompt}\n\n{EXTRA_RULES}"})
    
    payload = {"contents": [{"parts": parts}], "generationConfig": {"temperature": 0.2}}
    
    try:
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
        res_json = response.json()
        return res_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI LAYOUT ---
st.title("🛡️ RTL ARCHITECT PRO")
st.subheader("SystemVerilog Generation & Protocol Analysis")

with st.sidebar:
    st.header("🔑 Secure Connection")
    api_key = st.text_input("Gemini API Key", type="password", help="Using Gemini 2.5 Flash for maximum speed.")
    st.divider()
    mode = st.radio("Task Mode", ["Module Design", "Testbench Gen", "Expert Explanation"])
    uploaded_pdf = st.file_uploader("Reference Datasheet (PDF)", type="pdf")
    st.info("The PDF acts as the 'Source of Truth' for timing and signals.")

# Input Field
user_input = st.text_area("Functional Specification (Natural Language)", height=200, 
                          placeholder="Describe the module logic or K-map requirements here...")

if st.button("🚀 Generate Synthesizable RTL", type="primary"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        with st.spinner("Analyzing requirements with Flash speed..."):
            # Constructing the refined prompt
            task_prefix = "Reason through the logic first, then provide the SystemVerilog module."
            if mode == "Testbench Gen": task_prefix = "Generate a full SystemVerilog testbench with clock/reset."
            
            final_prompt = f"{task_prefix}\n\nInput Spec: {user_input}"
            
            raw_output = call_gemini_api(final_prompt, api_key, uploaded_pdf)
            
            # Displaying Reasoning and Code
            st.success("Generation Complete!")
            st.markdown("### 🧠 Design Reasoning")
            st.info(raw_output.split('```')[0]) # Display reasoning if it exists
            
            if '```' in raw_output:
                code_content = raw_output.split('```')[1].replace('systemverilog', '').replace('verilog', '')
                st.markdown("### 💻 SystemVerilog RTL")
                st.code(code_content, language="verilog")
