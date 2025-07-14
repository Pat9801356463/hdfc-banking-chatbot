import streamlit as st
from dotenv import load_dotenv

from utils.context_tracker import update_context_with_memory
from utils.rag_engine import load_documents_for_use_case, find_best_document
from utils.response_generator import generate_final_answer
from utils.session_manager import load_user_session
from utils.agent_orchestrator import orchestrate_agents
from utils.planner_agent import plan_tools_for_query
from utils.cache_manager import GlobalCache, is_public_query
from utils.debug_logger import add_log


load_dotenv()

st.set_page_config(page_title="💬 HDFC Banking Chatbot", layout="wide")

st.title("🏦 HDFC Banking Assistant (RAG + Agents + Gemini + Cache)")
st.markdown("Ask me anything about HDFC loans, credit cards, transactions, RBI circulars, KYC, etc.")

# --- Session Management ---
user_id = st.sidebar.text_input("👤 Enter User ID", value="001")

if user_id and "session_data" not in st.session_state:
    session, greeting = load_user_session(user_id)
    if session:
        st.session_state.session_data = session
        st.session_state.chat_history = []
        st.success(greeting)
    else:
        st.error(greeting)

# --- Chat Input ---
if "session_data" in st.session_state:
    query = st.chat_input("Ask your question...")

    if query:
        session = st.session_state.session_data
        debug_steps = [f"🔍 Query: {query}"]

        # Step 1: Classify intent + use case
        intent, use_case = update_context_with_memory(query, session)
        debug_steps.append(f"🧠 Intent: `{intent}`")
        debug_steps.append(f"📂 Use Case: `{use_case}`")

        # Step 2: Check cache
        cached = None
        if is_public_query(intent, use_case):
            cached = GlobalCache.get(query)
            if cached:
                debug_steps.append("💾 Cache Hit")
                final_response = cached
            else:
                debug_steps.append("💾 Cache Miss")

        if not cached:
            try:
                # Step 3: Use RAG (for supported use cases)
                context = load_documents_for_use_case(use_case)
                if "⚠️" in context or len(context.strip()) < 20:
                    raise ValueError("Weak RAG context")
                debug_steps.append("📚 RAG used for context")

                final_response = generate_final_answer(query, context, session["name"])
                debug_steps.append("✅ Gemini response from RAG")

            except Exception as rag_err:
                debug_steps.append(f"⚠️ RAG Failed: {rag_err}")
                # Step 4: Fallback to agent pipeline
                response = orchestrate_agents(query, use_case, user_name=session["name"])
                final_response = response
                debug_steps.append("🛠 Agentic fallback used")

            # Step 5: Cache (only if public)
            if is_public_query(intent, use_case):
                GlobalCache.set(query, final_response, use_case=use_case)

        # Step 6: Memory logging
        session["memory"].append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": "",  # omit full context in memory
            "response": final_response
        })
        st.session_state.chat_history.append({
            "query": query,
            "response": final_response
        })

        # Step 7: Log debug
        add_log(query, debug_steps)

# --- Chat Display ---
if "chat_history" in st.session_state:
    for item in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(item["query"])
        with st.chat_message("assistant"):
            st.markdown(item["response"])
