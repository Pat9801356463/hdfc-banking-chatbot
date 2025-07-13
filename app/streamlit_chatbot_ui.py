# app/streamlit_chatbot_ui.py

import streamlit as st
from utils.response_generator import generate_final_answer
from utils.cache_manager import GlobalCache, is_public_query
from utils.rag_engine import load_documents_for_use_case, find_best_document
from utils.agent_orchestrator import orchestrate_agents
from utils.planner_agent import plan_tools_for_query
from utils.intent_classifier import classify_query  # optional if not using

st.set_page_config(page_title="💬 HDFC Banking Chatbot", layout="wide")

st.title("💬 HDFC Banking Chatbot")
st.markdown("Ask me anything about HDFC loans, credit cards, RBI circulars, etc.")

# Track pipeline steps
debug_logs = []

with st.form("chat_form"):
    user_input = st.text_area("🧠 Your Query:", height=100)
    submitted = st.form_submit_button("Ask")

if submitted and user_input.strip():
    try:
        st.markdown("### 🧾 Debug Logs")
        debug_logs.append(f"🔍 Query: `{user_input}`")

        # Step 1: Load embeddings / docs (RAG base)
        use_case = load_documents_for_use_case(user_input)
        debug_logs.append(f"📚 Use Case: `{use_case}`")

        # Step 2: Classify public vs internal
        public = is_public_query(intent=None, use_case=use_case)
        debug_logs.append(f"🌐 Is Public Query? `{public}`")

        # Step 3: Check cache
        cached = GlobalCache.get(user_input)
        if cached:
            debug_logs.append("💾 Cache Hit")
            st.success("✅ Response (Cached)")
            st.write(cached)
        else:
            debug_logs.append("💾 Cache Miss")

            # Step 4: Choose between RAG or Agents
            if public:
                debug_logs.append("🛠 Using Agent Pipeline")
                tools = plan_tools_for_query(user_input)
                debug_logs.append(f"🔧 Tools Planned: {tools}")
                response = orchestrate_agents(user_input, use_case)
                debug_logs.append("🤖 Agent Pipeline Executed")
            else:
                debug_logs.append("📄 Using RAG (Document-Based)")
                matched_doc = find_best_document(user_input)
                if matched_doc:
                    response = generate_final_answer(user_input, matched_doc, user_name="Aditya Sharma")
                    debug_logs.append("📄 RAG Response Generated")
                else:
                    response = "⚠️ No relevant information found in RAG documents."
                    debug_logs.append("⚠️ RAG Failed: No matching doc")

            # Step 5: Show result
            st.success("✅ Final Answer")
            st.markdown(response)

    except Exception as e:
        st.error(f"❌ App Crashed: {e}")
        debug_logs.append(f"❌ Exception: {e}")

    # Step 6: Show debug logs
    with st.expander("🔎 Debug Trace", expanded=True):
        st.markdown("\n".join([f"- {log}" for log in debug_logs]))
