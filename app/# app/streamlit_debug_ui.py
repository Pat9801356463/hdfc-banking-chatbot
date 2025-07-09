# app/streamlit_debug_ui.py

import streamlit as st

from utils.rag_engine import load_documents_for_use_case, USECASE_DOC_PATHS
from utils.intent_mapper import classify_intent_and_usecase
from utils.session_manager import load_user_session
from utils.response_generator import generate_final_answer


st.set_page_config(page_title="RAG Engine Debugger", layout="wide")

st.title("📂 RAG Engine Debug UI")
st.markdown("Use this to validate document loading, intent mapping, and session flow.")

# --- RAG Section ---
st.subheader("📄 Load RAG Context")
use_case = st.selectbox("Select a Use Case", list(USECASE_DOC_PATHS.keys()))

if st.button("🔍 Load Documents"):
    with st.spinner("Loading documents..."):
        try:
            content = load_documents_for_use_case(use_case)
            st.success("✅ Documents loaded successfully!")
            st.text_area("🧾 Extracted Content Preview", content, height=500)
        except Exception as e:
            st.error(f"❌ Failed to load content:\n\n{e}")

# --- Intent Classification ---
st.divider()
st.subheader("🧠 Gemini Intent Classification")

test_query = st.text_input("Enter a sample user query:")
if test_query:
    result = classify_intent_and_usecase(test_query)
    st.json(result)

# --- User Session Preview ---
st.divider()
st.subheader("👤 Load User Session")

user_id = st.text_input("Enter user ID (e.g., 001):")
if user_id:
    session, greeting = load_user_session(user_id)
    if session:
        st.success(greeting)
        st.write("Recent Transactions:")
        st.dataframe(session["transactions"].tail(5))
    else:
        st.error(greeting)
