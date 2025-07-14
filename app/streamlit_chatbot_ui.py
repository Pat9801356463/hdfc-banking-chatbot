import os
import streamlit as st
from dotenv import load_dotenv

# Core utility imports
from utils.session_manager import load_user_session
from utils.context_tracker import update_context_with_memory
from utils.rag_engine import load_documents_for_use_case
from utils.response_generator import generate_final_answer

# Agentic fallback pipeline
from utils.agent_orchestrator import orchestrate_agents
from utils.planner_agent import plan_tools_for_query

# Cache layer
from utils.cache_manager import GlobalCache, is_public_query
from utils.debug_logger import add_log

# Load environment variables
load_dotenv()

# --- UI Config ---
st.set_page_config(page_title="🏦 HDFC Banking Assistant", layout="wide")
st.title("🏦 HDFC Banking Assistant (RAG + Agentic + Gemini + Cache)")
st.markdown("Ask anything related to loans, credit cards, RBI circulars, fraud, transactions, and more.")

# --- User Login ---
user_id = st.sidebar.text_input("👤 Enter User ID", value="001")

if user_id and "session_data" not in st.session_state:
    session, greeting = load_user_session(user_id)
    if session:
        st.session_state.session_data = session
        st.session_state.chat_history = []
        st.success(greeting)
    else:
        st.error(greeting)

# --- Chat Interface ---
if "session_data" in st.session_state:
    query = st.chat_input("Ask your question...")

    if query:
        session = st.session_state.session_data
        debug_steps = [f"🔍 Query: {query}"]

        # Step 1: Intent + Use Case
        intent, use_case = update_context_with_memory(query, session)
        debug_steps.append(f"🧠 Intent: `{intent}`")
        debug_steps.append(f"📂 Use Case: `{use_case}`")

        # Step 2: Global Cache
        cached = None
        if is_public_query(intent, use_case):
            cached = GlobalCache.get(query)
            if cached:
                final_response = cached
                debug_steps.append("💾 Cache Hit")
            else:
                debug_steps.append("💾 Cache Miss")

        # Step 3: RAG (document lookup)
        if not cached:
            try:
                context = load_documents_for_use_case(use_case)
                if "⚠️" in context or len(context.strip()) < 20:
                    raise ValueError("Weak RAG context")
                debug_steps.append("📚 RAG loaded successfully")
                final_response = generate_final_answer(query, context, session["name"])
                debug_steps.append("✅ Gemini generated from RAG")
            except Exception as rag_fail:
                debug_steps.append(f"⚠️ RAG failed: {rag_fail}")
                final_response = orchestrate_agents(query, use_case, user_name=session["name"])
                debug_steps.append("🛠 Fallback to Agent pipeline")

            # Step 4: Cache result if public
            if is_public_query(intent, use_case):
                GlobalCache.set(query, final_response, use_case=use_case)
                debug_steps.append("📦 Stored in cache")

        # Step 5: Memory + Chat log
        session["memory"].append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": "",  # Omitting full context
            "response": final_response
        })

        st.session_state.chat_history.append({
            "query": query,
            "response": final_response
        })

        add_log(query, debug_steps)

# --- Display Chat History ---
if "chat_history" in st.session_state:
    for msg in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(msg["query"])
        with st.chat_message("assistant"):
            st.markdown(msg["response"])
