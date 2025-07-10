# app/streamlit_chatbot_ui.py

import streamlit as st
import pandas as pd
from utils.session_manager import load_user_session
from utils.context_tracker import update_context_with_memory
from utils.rag_engine import load_documents_for_use_case
from utils.response_generator import generate_final_answer

st.set_page_config(page_title="💬 HDFC Banking Chatbot", layout="wide")

st.title("🏦 HDFC Banking Assistant (Gemini-Powered)")
st.markdown("Ask your banking-related queries. The assistant understands intent, loads relevant context, and answers via Gemini.")

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

# --- Chat Input ---
if "session_data" in st.session_state:
    query = st.chat_input("Ask me anything...")

    if query:
        session = st.session_state.session_data

        # Step 1: Infer intent and use case using memory-aware context tracker
        intent, use_case = update_context_with_memory(query, session)

        # Step 2: Load relevant context
        if use_case in [
            "Investment (non-sharemarket)",
            "Documentation & Process Query",
            "Loan Prepurchase Query",
            "Banking Norms",
            "KYC & Details Update",
            "Download Statement & Document",
        ]:
            context = load_documents_for_use_case(use_case)

        elif use_case == "Transaction History":
            context = session["transactions"].tail(5).to_string(index=False)

        elif use_case == "Mutual Funds & Tax Benefits":
            context = (
                "You have invested in ELSS and Tax Saver Mutual Funds. These are eligible for deductions under Section 80C. "
                "We can help you calculate benefits or suggest tax-saving funds."
            )

        elif use_case == "Fraud Complaint - Scenario":
            last_txn_context = None
            for mem in reversed(session["memory"]):
                if mem["use_case"] == "Transaction History":
                    last_txn_context = mem["context"]
                    break

            if last_txn_context:
                lines = [line for line in last_txn_context.strip().split("\n") if line]
                txn_number = len(lines)
                today_str = pd.Timestamp.today().strftime("%d-%m-%Y")
                ticket_id = f"{session['user_id']}-{today_str}-{txn_number:02}"

                context = (
                    f"Based on your recent transaction history:\n\n{last_txn_context}\n\n"
                    f"✅ A fraud complaint has been raised.\n"
                    f"🆔 Ticket ID: {ticket_id}"
                )
            else:
                context = "⚠️ No recent transactions found to raise a fraud complaint. Please check your transaction history first."

        else:
            context = "❓ No context available for this use case."

        # Step 3: Generate Gemini Response
        final_response = generate_final_answer(query, context, session["name"])

        # Step 4: Log interaction in memory
        memory_entry = {
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": context[:500],
            "response": final_response
        }

        st.session_state.chat_history.append(memory_entry)
        session["memory"].append(memory_entry)

# --- Show Chat Messages ---
if "chat_history" in st.session_state:
    for item in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(item["query"])
        with st.chat_message("assistant"):
            st.markdown(item["response"])
