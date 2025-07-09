# app/streamlit_debug_ui.py

import os
import sys
import streamlit as st
import importlib.util
from pathlib import Path

# === [1] Resolve Repo Root ===
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parent.parent  # Goes from /app to repo root

# === [2] Dynamic Module Importer ===
def load_utils_module(module_name, relative_path_from_root):
    module_path = REPO_ROOT / relative_path_from_root
    if not module_path.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")
    
    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# === [3] Load all required utils/*.py modules ===
try:
    rag_engine = load_utils_module("rag_engine", "utils/rag_engine.py")
    intent_mapper = load_utils_module("intent_mapper", "utils/intent_mapper.py")
    session_manager = load_utils_module("session_manager", "utils/session_manager.py")
    response_generator = load_utils_module("response_generator", "utils/response_generator.py")
except Exception as e:
    st.error(f"❌ Critical Import Error:\n\n{e}")
    st.stop()

# === [4] Streamlit UI ===
st.set_page_config(page_title="RAG Engine Debugger", layout="wide")

st.title("📂 RAG Engine Debug UI")
st.markdown("Use this to validate document loading, intent mapping, and session flow.")

# --- RAG Section ---
st.subheader("📄 Load RAG Context")
use_case = st.selectbox("Select a Use Case", list(rag_engine.USECASE_DOC_PATHS.keys()))

if st.button("🔍 Load Documents"):
    with st.spinner("Loading documents..."):
        try:
            content = rag_engine.load_documents_for_use_case(use_case)
            st.success("✅ Documents loaded successfully!")
            st.text_area("🧾 Extracted Content Preview", content, height=500)
        except Exception as e:
            st.error(f"❌ Failed to load content:\n\n{e}")

# --- Intent Classification ---
st.divider()
st.subheader("🧠 Gemini Intent Classification")

test_query = st.text_input("Enter a sample user query:")
if test_query:
    result = intent_mapper.classify_intent_and_usecase(test_query)
    st.json(result)

# --- User Session Preview ---
st.divider()
st.subheader("👤 Load User Session")

user_id = st.text_input("Enter user ID (e.g., 001):")
if user_id:
    session, greeting = session_manager.load_user_session(user_id)
    if session:
        st.success(greeting)
        st.write("Recent Transactions:")
        st.dataframe(session["transactions"].tail(5))
    else:
        st.error(greeting)
