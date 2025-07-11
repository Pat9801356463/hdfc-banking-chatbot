import streamlit as st
import pandas as pd

from utils.session_manager import load_user_session
from utils.context_tracker import update_context_with_memory
from utils.rag_engine import load_documents_for_use_case
from utils.response_generator import generate_final_answer
from utils.web_retriever import (
    get_rbi_latest_circulars,
    get_rbi_interest_rates,
    get_hdfc_credit_cards,
    format_circulars,
    format_credit_cards,
    format_interest_rates,
    resolve_link_via_gemini,
)
from utils.cache_manager import GlobalCache, is_public_query

st.set_page_config(page_title="💬 HDFC Banking Chatbot", layout="wide")

st.title("🏦 HDFC Banking Assistant (RAG + Cohere + Gemini + Cache)")
st.markdown("Ask your banking-related queries. The assistant uses RAG, web data, Gemini, and caching for fast answers.")

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

        # Step 1: Intent + Use Case
        intent, use_case = update_context_with_memory(query, session)

        # Step 2: Global cache check for public queries
        cached = None
        if is_public_query(intent, use_case):
            cached = GlobalCache.get(query)

        if cached:
            context = cached
        else:
            try:
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
                        "📊 You have invested in ELSS and Tax Saver Mutual Funds. Eligible under Section 80C.\n"
                        "We can assist in tax-saving strategies."
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
                            f"✅ A fraud complaint has been raised.\n🆚 Ticket ID: {ticket_id}"
                        )
                    else:
                        context = "⚠️ No recent transactions found to raise a fraud complaint."

                elif "rbi circulars" in query.lower():
                    circulars = get_rbi_latest_circulars()
                    context = f"📜 Latest RBI Circulars:\n{format_circulars(circulars)}"

                elif "credit card" in query.lower():
                    cards = get_hdfc_credit_cards()
                    if isinstance(cards, list) and len(cards) == 1 and cards[0].startswith("http"):
                        context = f"🔗 Please refer to the official credit card page: {cards[0]}"
                    else:
                        context = f"💳 HDFC Credit Cards:\n{format_credit_cards(cards)}"

                elif "interest rate" in query.lower():
                    rates = get_rbi_interest_rates()
                    if any("http" in v for v in rates.values()):
                        context = f"🔗 You can check RBI interest rates at: {list(rates.values())[0]}"
                    else:
                        context = f"📈 RBI Interest Rates:\n{format_interest_rates(rates)}"

                else:
                    link_response = resolve_link_via_gemini(query)
                    if "http" in link_response:
                        context = f"🔗 Please refer to the following resource: {link_response}"
                    else:
                        context = f"{link_response}\n\nIf this doesn't answer your question, please clarify further."

                # Store in global cache if it's public and successful
                if is_public_query(intent, use_case):
                    GlobalCache.set(query, context)

            except Exception as e:
                context = f"⚠️ Failed to fetch relevant context due to: {e}"

        # Step 3: Gemini Response
        final_response = generate_final_answer(query, context, session["name"])

        # Step 4: Memory
        st.session_state.chat_history.append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": context[:500],
            "response": final_response
        })
        session["memory"].append(st.session_state.chat_history[-1])

# --- Display Chat History ---
if "chat_history" in st.session_state:
    for item in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(item["query"])
        with st.chat_message("assistant"):
            st.markdown(item["response"])

