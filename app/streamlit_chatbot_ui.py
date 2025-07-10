# app/streamlit_chatbot_ui.py

import streamlit as st
import pandas as pd
from utils.session_manager import load_user_session
from utils.intent_mapper import classify_intent_and_usecase
from utils.rag_engine import load_documents_for_use_case
from utils.response_generator import generate_final_answer

st.set_page_config(page_title="🤖 HDFC Chatbot", layout="wide")
st.title("🤖 HDFC Banking Chatbot")

# Initialize session state if needed
if "session" not in st.session_state:
    st.session_state.session = None
    st.session_state.memory = []

# Step 1: User login
with st.sidebar:
    st.header("👤 User Login")
    user_id = st.text_input("Enter User ID", value="001")
    if st.button("🔓 Load Session"):
        session, greeting = load_user_session(user_id)
        if session:
            st.session_state.session = session
            st.success(greeting)
        else:
            st.error(greeting)

# Main chatbot interaction
if st.session_state.session:
    st.markdown("---")
    st.subheader("💬 Ask Your Query")
    query = st.text_input("Your Query", value="Show my last 5 transactions")

    if st.button("💡 Get Response") and query:
        session = st.session_state.session

        # Step 1: Classify
        classification = classify_intent_and_usecase(query)
        intent = classification["intent"]
        use_case = classification["use_case"]

        # Step 2: Load context
        if use_case in [
            "Investment (non-sharemarket)",
            "Documentation & Process Query",
            "Loan Prepurchase Query",
            "Banking Norms",
            "KYC & Details Update",
            "Download Statement & Document"]:
            context = load_documents_for_use_case(use_case)

        elif use_case == "Transaction History":
            context = session["transactions"].tail(5).to_string(index=False)

        elif use_case == "Mutual Funds & Tax Benefits":
            context = "You have invested in ELSS and Tax Saver Mutual Funds. These are eligible for deductions under Section 80C. " \
                      "We can help you calculate benefits or suggest tax-saving funds."

        elif use_case == "Fraud Complaint - Scenario":
            last_txn_context = None
            for mem in reversed(st.session_state.memory):
                if mem["use_case"] == "Transaction History":
                    last_txn_context = mem["context"]
                    break

            if last_txn_context:
                lines = [line for line in last_txn_context.strip().split("\n") if line]
                txn_number = len(lines)
                today_str = pd.Timestamp.today().strftime("%d-%m-%Y")
                ticket_id = f"{session['user_id']}-{today_str}-{txn_number:02}"
                context = f"Based on your recent transaction history:\n\n{last_txn_context}\n\n" \
                          f"✅ A fraud complaint has been raised.\n🆔 Ticket ID: {ticket_id}"
            else:
                context = "⚠️ No recent transactions found to raise a fraud complaint. Please check your transaction history first."
        else:
            context = "❓ No context available for this use case."

        # Step 3: Generate response
        final_response = generate_final_answer(query, context, session["name"])

        # Step 4: Store in memory
        st.session_state.memory.append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": context[:500],
            "response": final_response
        })

        # Display results
        st.markdown("---")
        st.markdown(f"**🧠 Intent:** `{intent}`")
        st.markdown(f"**📂 Use Case:** `{use_case}`")
        st.markdown("**🤖 Gemini Response:**")
        st.success(final_response)

# Memory View
if st.session_state.memory:
    st.markdown("---")
    st.subheader("📝 Conversation Summary")
    for i, item in enumerate(st.session_state.memory[::-1], 1):
        with st.expander(f"{i}. {item['query']}"):
            st.markdown(f"**Intent:** {item['intent']}")
            st.markdown(f"**Use Case:** {item['use_case']}")
            st.markdown(f"**Response:** {item['response']}")
