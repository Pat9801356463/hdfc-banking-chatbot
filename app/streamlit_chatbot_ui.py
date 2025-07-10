# app/streamlit_chatbot_ui.py

import streamlit as st
from utils.session_manager import load_user_session
from utils.intent_mapper import classify_intent_and_usecase
from utils.rag_engine import load_documents_for_use_case
from utils.response_generator import generate_final_answer
import pandas as pd

st.set_page_config(page_title="💬 HDFC Chatbot", layout="wide")
st.title("💬 HDFC Banking Assistant")

# ---- Sidebar: User Login ----
with st.sidebar:
    st.header("👤 Login")
    user_id = st.text_input("Enter User ID", value=st.session_state.get("user_id", "001"))
    if st.button("🔐 Load Session"):
        session, greeting = load_user_session(user_id)
        if session:
            st.session_state.user_id = user_id
            st.session_state.session = session
            st.session_state.chat_history = []  # Reset chat history
            st.success(greeting)
        else:
            st.error(greeting)

# ---- Main Chat Area ----
if "session" not in st.session_state:
    st.warning("Please login using a valid User ID from the sidebar.")
    st.stop()

# Initialize chat memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous conversation
for msg in st.session_state.chat_history:
    st.chat_message("user").markdown(msg["query"])
    st.chat_message("assistant").markdown(msg["response"])

# Input box for new message
user_query = st.chat_input("Ask a banking question...")

if user_query:
    session = st.session_state.session

    # Step 1: Intent & Use Case
    classification = classify_intent_and_usecase(user_query)
    intent = classification["intent"]
    use_case = classification["use_case"]

    # Step 2: Context Retrieval
    if use_case in [
        "Investment (non-sharemarket)",
        "Documentation & Process Query",
        "Loan Prepurchase Query",
        "Banking Norms",
        "KYC & Details Update",
        "Download Statement & Document"
    ]:
        context = load_documents_for_use_case(use_case)

    elif use_case == "Transaction History":
        context = session["transactions"].tail(5).to_string(index=False)

    elif use_case == "Mutual Funds & Tax Benefits":
        context = (
            "You have invested in ELSS and Tax Saver Mutual Funds. "
            "These are eligible for deductions under Section 80C."
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
            context = f"Recent transactions:\n{last_txn_context}\n\n✅ Fraud complaint raised.\n🆔 Ticket ID: {ticket_id}"
        else:
            context = "⚠️ No recent transactions found. Please check your transaction history first."

    else:
        context = "❓ No context available for this use case."

    # Step 3: Generate Answer
    response = generate_final_answer(user_query, context, session["name"])

    # Step 4: Update memory
    session["memory"].append({
        "query": user_query,
        "intent": intent,
        "use_case": use_case,
        "context": context[:500],
        "response": response
    })

    # Step 5: Add to UI chat history
    st.chat_message("user").markdown(user_query)
    st.chat_message("assistant").markdown(response)
    st.session_state.chat_history.append({
        "query": user_query,
        "response": response
    })
