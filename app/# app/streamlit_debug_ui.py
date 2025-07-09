# app/streamlit_debug_ui.py

import os
import sys
import streamlit as st
import importlib.util

# Utility to dynamically import any utils module
def load_utils_module(module_name, file_path):
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), file_path))
    spec = importlib.util.spec_from_file_location(module_name, abs_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load all required modules
rag_engine = load_utils_module("rag_engine", "../utils/rag_engine.py")
intent_mapper = load_utils_module("intent_mapper", "../utils/intent_mapper.py")
session_manager = load_utils_module("session_manager", "../utils/session_manager.py")
response_generator = load_utils_module("response_generator", "../utils/response_generator.py")

# Start Streamlit UI
st.set_page_config(page_title="RAG Engine Debugger", layout="wide")

st.title("📂 RAG Engine Debug UI")
st.markdown("Use this to validate document loading for each use case and modules.")

use_case = st.selectbox("Select a Use Case", list(rag_engine.USECASE_DOC_PATHS.keys()))

if st.button("🔍 Load Documents"):
    with st.spinner("Loading documents..."):
        try:
            content = rag_engine.load_documents_for_use_case(use_case)
            st.success("✅ Documents loaded successfully!")
            st.text_area("🧾 Extracted Content Preview", content, height=500)
        except Exception as e:
            st.error(f"❌ Failed to load content:\n\n{e}")

# Optional test block for intent or session
st.divider()
st.markdown("### 🔍 Test Other Modules (Optional)")

test_query = st.text_input("Type a test query to classify intent:")
if test_query:
    result = intent_mapper.classify_intent_and_usecase(test_query)
    st.json(result)

user_id = st.text_input("Test loading a user session (e.g., 001):")
if user_id:
    session, greeting = session_manager.load_user_session(user_id)
    if session:
        st.success(f"Loaded session for {session['name']}")
        st.dataframe(session["transactions"].head())
    else:
        st.warning(greeting)
