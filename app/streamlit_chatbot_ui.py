# app/streamlit_chatbot_ui.py

import streamlit as st
from app.utils.session_manager import load_user_session
from app.utils.intent_mapper import classify_intent_and_usecase
from app.utils.rag_engine import load_documents_for_use_case
from app.utils.response_generator import generate_final_answer
import pandas as pd

# App configuration
st.set_page_config(page_title="💬 HDFC Chatbot UI", layout="wide")
st.title("🤖 HDFC Banking Assistant")

# Initialize session state
if "session" not in st.session_state:
    st.session_state.session = None
if "current_use_case" not in st.session_state:
    st.session_state.current_use_case = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ USER LOGIN ------------------
with st.sidebar:
    st.header("👤 User Login")
    user_id = st.text_input("Enter your User ID", value="001")
    if st.button("🔓 Load Session"):
        session, greeting = load_user_session(user_id)
        if session:
            st.session_state.session = session
            st.success(greeting)
        else:
            st.error(greeting)

# ------------------ MAIN CHAT ------------------
if st.session_state.session:
    st.subheader(f"Hello, {st.session_state.session['name']}! How can I assist you today?")
    user_query = st.text_input("💬 Your Message")

    if st.button("➡️ Send") and user_query:
        # Step 1: Intent classification
        classification = classify_intent_and_usecase(user_query)
        intent = classification["intent"]
        use_case = classification["use_case"]

        # Step 2: Maintain continuity if use_case is too vague
        if use_case == "General Query" and st.session_state.current_use_case:
            use_case = st.session_state.current_use_case
        else:
            st.session_state.current_use_case = use_case

        # Step 3: Context gathering
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
            context = st.session_state.session["transactions"].tail(5).to_string(index=False)

        elif use_case == "Mutual Funds & Tax Benefits":
            context = "You have invested in ELSS and Tax Saver Mutual Funds, eligible under Section 80C. " \
                      "HDFC Bank offers a range of SIPs that can help you save tax."

        elif use_case == "Fraud Complaint - Scenario":
            last_txn_context = None
            for mem in reversed(st.session_state.session["memory"]):
                if mem["use_case"] == "Transaction History":
                    last_txn_context = mem["context"]
                    break
            if last_txn_context:
                txn_number = len([line for line in last_txn_context.splitlines() if line.strip()])
                today_str = pd.Timestamp.today().strftime("%d-%m-%Y")
                ticket_id = f"{st.session_state.session['user_id']}-{today_str}-{txn_number:02}"
                context = f"Based on your transaction history:\n\n{last_txn_context}\n\n" \
                          f"✅ A fraud complaint has been raised.\n🆔 Ticket ID: {ticket_id}"
            else:
                context = "⚠️ No recent transactions found to raise a fraud complaint."

        else:
            context = "❓ No relevant documents or context available."

        # Step 4: Generate answer using Gemini
        past_context = "\n\n".join(
            f"User: {mem['query']}\nBot: {mem['response']}"
            for mem in st.session_state.session["memory"][-3:]
        )

        final_response = generate_final_answer(
            query=user_query,
            context=context,
            user_name=st.session_state.session["name"],
            past_turns=past_context
        )

        # Step 5: Store in memory
        st.session_state.session["memory"].append({
            "query": user_query,
            "intent": intent,
            "use_case": use_case,
            "context": context[:500],
            "response": final_response
        })

        # Step 6: Show chat
        st.session_state.chat_history.append((user_query, final_response))

    # Display the chat history
    for user_msg, bot_msg in reversed(st.session_state.chat_history):
        st.markdown(f"**🧑 You:** {user_msg}")
        st.markdown(f"**🤖 Bot:** {bot_msg}")

    # Optional debug
    if st.checkbox("🧠 Show Memory", value=False):
        st.json(st.session_state.session["memory"], expanded=False)

else:
    st.warning("Please login using your User ID from the sidebar to begin.")
