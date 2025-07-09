import streamlit as st

# ✅ Correct relative imports (assuming utils is inside app/)
from utils.rag_engine import load_documents_for_use_case, USECASE_DOC_PATHS
from utils.intent_mapper import classify_intent_and_usecase
from utils.session_manager import load_user_session
from utils.response_generator import generate_final_answer

# Page Config
st.set_page_config(page_title="📂 RAG Engine Debugger", layout="wide")

st.title("🔍 HDFC Banking Chatbot - Debug UI")
st.markdown("Use this interface to validate document loading, intent detection, session load, and Gemini responses.")

# Tabs for modular testing
tab1, tab2, tab3, tab4 = st.tabs(["📂 RAG Loader", "🧠 Intent Mapper", "👤 Session Loader", "🤖 Full Response"])

# ====================== 📂 RAG Loader ========================
with tab1:
    st.header("📂 Load Documents by Use Case")
    use_case = st.selectbox("Select a Use Case", list(USECASE_DOC_PATHS.keys()))

    if st.button("🔍 Load Documents", key="load_docs"):
        with st.spinner("Loading documents..."):
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
