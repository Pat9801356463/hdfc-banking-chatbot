# streamlit_debug_ui.py

import os
import streamlit as st
from dotenv import load_dotenv

# Local imports
from app.debug_logger import get_logs
from utils.rag_engine import load_documents_for_use_case, USECASE_DOC_PATHS
from utils.intent_mapper import classify_intent_and_usecase
from utils.session_manager import load_user_session
from utils.response_generator import generate_final_answer

# Load env variables
load_dotenv()

# Streamlit page config
st.set_page_config(page_title="🛠️ Debug Console", layout="wide")
st.title("🧠 HDFC Chatbot Debug Console")

# -------------------- 🪵 Live Logs Viewer ---------------------
st.subheader("📋 Live Logs")
logs = get_logs()
if not logs:
    st.info("No logs available yet. Interact with the chatbot first.")
else:
    for i, entry in enumerate(logs[::-1]):
        with st.expander(f"🔍 Query: {entry['query']}"):
            for step in entry['steps']:
                st.markdown(f"- {step}")

st.markdown("---")

# -------------------- 🧪 Test Modules ---------------------
tab1, tab2, tab3, tab4 = st.tabs(["📂 RAG Loader", "🧠 Intent Mapper", "👤 Session Loader", "🤖 Final Response"])

# ========== 📂 Tab 1: RAG Loader ==========
with tab1:
    st.header("📂 Load Documents by Use Case")
    use_case = st.selectbox("Select a Use Case", list(USECASE_DOC_PATHS.keys()))
    if st.button("🔍 Load Documents"):
        with st.spinner("Loading documents..."):
            docs = load_documents_for_use_case(use_case)
            st.success(f"{len(docs)} document chunks loaded.")
            for i, doc in enumerate(docs[:10]):
                st.markdown(f"**Chunk {i+1}:** {doc.page_content[:300]}...")

# ========== 🧠 Tab 2: Intent Mapper ==========
with tab2:
    st.header("🧠 Test Intent & Use-Case Mapper")
    user_query = st.text_input("Enter a user query:")
    if st.button("🧭 Classify Intent"):
        if user_query.strip():
            with st.spinner("Classifying..."):
                intent, use_case = classify_intent_and_usecase(user_query)
                st.success("Classification complete")
                st.markdown(f"- **Intent**: `{intent}`")
                st.markdown(f"- **Use Case**: `{use_case}`")
        else:
            st.warning("Enter a query first.")

# ========== 👤 Tab 3: Session Loader ==========
with tab3:
    st.header("👤 Load Sample User Session")
    sample_name = st.text_input("Enter username (e.g. Aditya Sharma)", value="Aditya Sharma")
    if st.button("📦 Load Session"):
        with st.spinner("Retrieving session data..."):
            session_data = load_user_session(sample_name)
            if session_data:
                st.json(session_data)
            else:
                st.warning("No session found.")

# ========== 🤖 Tab 4: Final Answer Generator ==========
with tab4:
    st.header("🤖 Test Full Final Answer Generator")
    raw_query = st.text_area("Enter user query:")
    mock_data = st.text_area("Enter mock structured data (JSON or text):")

    if st.button("🪄 Generate Answer"):
        if raw_query.strip() and mock_data.strip():
            with st.spinner("Generating response..."):
                response = generate_final_answer(raw_query, mock_data, user_name="Aditya Sharma")
                st.success("Generated response:")
                st.write(response)
        else:
            st.warning("Please enter both query and mock data.")

            try:
                content = load_documents_for_use_case(use_case)
                st.success("✅ Documents loaded successfully!")
                st.text_area("📄 Extracted Content", content, height=400)
            except Exception as e:
                st.error(f"❌ Failed to load content: {e}")

# ====================== 🧠 Intent Mapper ========================
with tab2:
    st.header("🧠 Test Intent and Use Case Classifier")
    test_query = st.text_input("Enter a sample user query", value="Can I see my last 5 transactions?")

    if st.button("⚡ Classify Intent", key="intent_btn"):
        with st.spinner("Classifying with Gemini..."):
            result = classify_intent_and_usecase(test_query)
            st.success("✅ Intent classified.")
            st.write("**Intent:**", result.get("intent"))
            st.write("**Use Case:**", result.get("use_case"))

# ====================== 👤 Session Loader ========================
with tab3:
    st.header("👤 Load Session Data")
    user_id = st.text_input("Enter User ID", value="001")

    if st.button("📥 Load Session", key="session_btn"):
        session, greeting = load_user_session(user_id)
        if session:
            st.success(greeting)
            st.write("**User Name:**", session["name"])
            st.write("**Recent Transactions:**")
            st.dataframe(session["transactions"].tail(5))
        else:
            st.error(greeting)

# ====================== 🤖 Full Response Gen ========================
with tab4:
    st.header("🤖 Simulate Final Response from Gemini")
    user_query = st.text_input("Query", value="What documents do I need for a loan?")
    selected_use_case = st.selectbox("Select Use Case", list(USECASE_DOC_PATHS.keys()), key="full_usecase")

    if st.button("💬 Generate Response"):
        with st.spinner("Retrieving context & generating answer..."):
            try:
                context = load_documents_for_use_case(selected_use_case)
                response = generate_final_answer(user_query, context, user_name="TestUser")
                st.success("✅ Response generated")
                st.markdown(f"**Gemini Response:**\n\n{response}")
            except Exception as e:
                st.error(f"❌ Failed to generate: {e}")

