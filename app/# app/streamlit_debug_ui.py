# app/streamlit_debug_ui.py

import sys
import os

# Step 1: Add root path to sys.path so "utils" is discoverable
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st

# Step 2: Try importing with a safe fallback
try:
    from utils.rag_engine import load_documents_for_use_case, USECASE_DOC_PATHS
except ModuleNotFoundError as e:
    st.error(f"❌ Import Error: Could not import from 'utils'.\n\n{e}")
    st.stop()

# Step 3: UI Setup
st.set_page_config(page_title="RAG Engine Debugger", layout="wide")

st.title("📂 RAG Engine Debug UI")
st.markdown("Use this to validate document loading for each use case.")

# Dropdown to select a use case
use_case = st.selectbox("Select a Use Case", list(USECASE_DOC_PATHS.keys()))

# Load and display content
if st.button("🔍 Load Documents"):
    with st.spinner("Loading documents..."):
        try:
            content = load_documents_for_use_case(use_case)
            st.success("✅ Documents loaded successfully!")
            st.text_area("🧾 Extracted Content Preview", content, height=500)
        except Exception as e:
            st.error(f"❌ Failed to load content:\n\n{e}")
