# app/streamlit_debug_ui.py

import sys
import os

# Fix for Streamlit Cloud: Add repo root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from utils.rag_engine import load_documents_for_use_case, USECASE_DOC_PATHS

st.set_page_config(page_title="RAG Engine Debugger", layout="wide")

st.title("📂 RAG Engine Debug UI")
st.markdown("Use this to validate document loading for each use case.")

# Dropdown to select a use case
use_case = st.selectbox("Select a Use Case", list(USECASE_DOC_PATHS.keys()))

if st.button("🔍 Load Documents"):
    with st.spinner("Loading documents..."):
        try:
            content = load_documents_for_use_case(use_case)
            st.success("Documents loaded successfully!")
            st.text_area("🧾 Preview Extracted Content", content, height=500)
        except Exception as e:
            st.error(f"❌ Failed to load content: {e}")
