import streamlit as st
import PyPDF2
import pandas as pd
import docx
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# -----------------------
# Setup OpenAI Client
# -----------------------
# Set your API key in environment variables (recommended)
# Example (Windows PowerShell):
#   setx OPENAI_API_KEY "your_api_key_here"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Function: Extract text from PDF
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# --- Function: Extract text from Word DOCX
def read_docx(file):
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# --- Function: Extract text from CSV & Excel
def read_table(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df.to_string()

# --- AI Autonomous Analysis
def analyze_document(content):
    prompt = f"""
    You are an autonomous audit assistant.
    Your mission:
    1. Summarize the document.
    2. Point out any missing information that could affect an audit.
    3. Suggest the next action for the auditor.

    Document content:
    {content[:4000]}  # limit to avoid token overflow
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI auditor."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content

# -----------------------
# STREAMLIT UI
# -----------------------
st.set_page_config(page_title="Agentic AI File Intake Assistant", page_icon="📂", layout="centered")
st.title("📂 Agentic AI – Intelligent File Intake Assistant")

uploaded_file = st.file_uploader("Upload a PDF, Word, CSV, or Excel file", type=["pdf", "docx", "csv", "xlsx"])

if uploaded_file:
    # Extract content
    if uploaded_file.name.endswith(".pdf"):
        content = read_pdf(uploaded_file)
    elif uploaded_file.name.endswith(".docx"):
        content = read_docx(uploaded_file)
    else:
        content = read_table(uploaded_file)

    st.subheader("📄 Extracted Content (Preview)")
    st.write(content[:1000] + "..." if len(content) > 1000 else content)

    with st.spinner("🤖 Analyzing document..."):
        ai_result = analyze_document(content)

    st.subheader("🔍 AI Agent Analysis")
    st.write(ai_result)
