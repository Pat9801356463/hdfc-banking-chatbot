import streamlit as st
import pandas as pd

from utils.session_manager import load_user_session
from utils.context_tracker import update_context_with_memory
from utils.rag_engine import load_documents_for_use_case
from utils.response_generator import generate_final_answer
# from utils.web_retriever import (
#     get_rbi_latest_circulars,
#     get_rbi_interest_rates,
#     get_hdfc_credit_cards,
#     format_circulars,
#     format_credit_cards,
#     format_interest_rates,
#     resolve_link_via_gemini,
# )

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

        # Step 1: Intent + use case inference
        intent, use_case = update_context_with_memory(query, session)

        # Step 2: Context loading (Simulated mode)
        try:
            if "credit card" in query.lower():
                # cards = get_hdfc_credit_cards()
                # context = "Here are some popular HDFC credit cards:\n" + format_credit_cards(cards)
                context = "💳 HDFC Credit Cards:\n- Regalia\n- Millennia\n- Infinia\n(📎 Simulated response)"

            elif "rbi circular" in query.lower():
                # circulars = get_rbi_latest_circulars()
                # context = "Here are the latest RBI circulars:\n" + format_circulars(circulars)
                context = "📜 Latest RBI Circulars:\n- Monetary Policy July 2025\n- Repo Rate Guidelines\n(📎 Simulated response)"

            elif "interest rate" in query.lower():
                # rates = get_rbi_interest_rates()
                # context = "Here are the latest interest rates from RBI:\n" + format_interest_rates(rates)
                context = "📈 RBI Interest Rates:\n- Repo Rate: 6.50%\n- Reverse Repo: 3.35%\n(📎 Simulated response)"

            elif use_case in [
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
                    "📊 You have invested in ELSS and Tax Saver Mutual Funds. Eligible under Section 80C. "
                    "We can assist in tax-saving strategies. (Simulated)"
                )

            elif use_case == "Fraud Complaint - Scenario":
                last_txn_context = next(
                    (mem["context"] for mem in reversed(session["memory"])
                     if mem["use_case"] == "Transaction History"),
                    None
                )
                if last_txn_context:
                    txn_number = len([line for line in last_txn_context.strip().split("\n") if line])
                    today_str = pd.Timestamp.today().strftime("%d-%m-%Y")
                    ticket_id = f"{session['user_id']}-{today_str}-{txn_number:02}"
                    context = (
                        f"Based on your recent transaction history:\n\n{last_txn_context}\n\n"
                        f"✅ A fraud complaint has been raised.\n"
                        f"🆔 Ticket ID: {ticket_id} (Simulated)"
                    )
                else:
                    context = "⚠️ No recent transactions found to raise a fraud complaint."

            else:
                # try:
                #     link_response = resolve_link_via_gemini(query)
                #     if link_response.startswith("http"):
                #         context = f"🔗 Please refer to the following resource: {link_response}"
                #     else:
                #         context = f"{link_response}\n\nIf this doesn't answer your question, please clarify further."
                # except Exception as e:
                #     context = "⚠️ Gemini failed to retrieve a URL. Please try again later."
                context = "🔗 Here's a useful link that may help (📎 Simulated Gemini response)."

        except Exception as e:
            context = f"⚠️ Unable to load context due to: {e}"

        # Step 3: Generate final answer
        final_response = generate_final_answer(query, context, session["name"])

        # Step 4: Store memory
        st.session_state.chat_history.append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": context[:500],
            "response": final_response
        })
        session["memory"].append(st.session_state.chat_history[-1])

# --- Show chat history ---
if "chat_history" in st.session_state:
    for item in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(item["query"])
        with st.chat_message("assistant"):
            st.markdown(item["response"])
