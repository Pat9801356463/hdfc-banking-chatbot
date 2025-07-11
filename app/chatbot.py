# 🔄 Updated chatbot.py with global cache integration

from utils.session_manager import load_user_session
from utils.context_tracker import update_context_with_memory
from utils.rag_engine import load_documents_for_use_case
from utils.response_generator import generate_final_answer
from utils.web_retriever import (
    get_hdfc_credit_cards,
    get_rbi_latest_circulars,
    get_rbi_interest_rates,
    format_circulars,
    format_credit_cards,
    format_interest_rates,
    resolve_link_via_gemini,
)
from utils.cohere_helper import classify_intent_usecase_cohere
from utils.cache_manager import GlobalCache
import pandas as pd

# Initialize global public query cache
global_cache = GlobalCache()

# Basic classifier for public info use cases
def is_public_query(use_case):
    public_usecases = [
        "Documentation & Process Query",
        "KYC & Details Update",
        "Banking Norms",
        "Download Statement & Document",
        "Mutual Funds & Tax Benefits",
        "Loan Prepurchase Query",
        "Investment (non-sharemarket)"
    ]
    return use_case in public_usecases

def main():
    print("🟢 Welcome to the HDFC Banking Assistant\n")

    user_id = input("Enter your User ID (e.g. 001): ").strip()
    session, greeting = load_user_session(user_id)

    if session is None:
        print(greeting)
        return

    print(greeting)

    while True:
        query = input("\n💬 Your Query (or type 'exit' to quit): ").strip()
        if query.lower() in ['exit', 'quit']:
            break

        # Step 1: Classify query
        classification = classify_intent_usecase_cohere(query)
        intent = classification.get("intent", "unknown")
        use_case = classification.get("use_case", "unknown")

        print(f"🧠 Intent: {intent}")
        print(f"📂 Use Case: {use_case}")

        # Step 2: Check cache for public queries
        context = None
        if is_public_query(use_case):
            cached = global_cache.get(query)
            if cached:
                print("⚡ Response served from cache!")
                print(f"\n🤖 {cached}\n")
                continue

        # Step 3: Try RAG
        try:
            context = load_documents_for_use_case(use_case)
            if "⚠️" in context or len(context.strip()) < 20:
                raise ValueError("RAG context too weak")

        except Exception:
            try:
                if use_case == "Transaction History":
                    context = session["transactions"].tail(5).to_string(index=False)

                elif use_case == "Mutual Funds & Tax Benefits":
                    context = (
                        "You have invested in ELSS and Tax Saver Mutual Funds. These are eligible for deductions under Section 80C. "
                        "We can help you calculate benefits or suggest tax-saving funds."
                    )

                elif use_case == "Fraud Complaint - Scenario":
                    last_txn_context = next(
                        (mem.get("context") for mem in reversed(session["memory"])
                         if mem.get("use_case") == "Transaction History"),
                        None
                    )
                    if last_txn_context:
                        txn_number = len([line for line in last_txn_context.strip().split("\n") if line])
                        today_str = pd.Timestamp.today().strftime("%d-%m-%Y")
                        ticket_id = f"{session['user_id']}-{today_str}-{txn_number:02}"
                        context = (
                            f"Based on your recent transaction history:\n\n{last_txn_context}\n\n"
                            f"✅ A fraud complaint has been raised.\n🆔 Ticket ID: {ticket_id}"
                        )
                    else:
                        context = "⚠️ No recent transactions found to raise a fraud complaint."

                elif "rbi circulars" in query.lower():
                    circulars = get_rbi_latest_circulars()
                    context = f"Here are the latest RBI circulars:\n{format_circulars(circulars)}"

                elif "credit card" in query.lower():
                    cards = get_hdfc_credit_cards()
                    context = f"HDFC Bank offers the following credit cards:\n{format_credit_cards(cards)}"

                elif "interest rate" in query.lower():
                    rates = get_rbi_interest_rates()
                    context = f"Latest RBI Interest Rates:\n{format_interest_rates(rates)}"

                else:
                    context = resolve_link_via_gemini(query)

            except Exception as e:
                context = f"⚠️ Failed to fetch relevant context due to: {e}"

        # Step 4: Generate answer
        final_response = generate_final_answer(query, context, session["name"])

        # Step 5: Log memory
        session["memory"].append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": context[:500],
            "response": final_response
        })

        # Step 6: Cache public queries
        if is_public_query(use_case):
            global_cache.add(query, final_response)

        print(f"\n🤖 {final_response}\n")

    print("\n🗒️ Session Summary:")
    for i, item in enumerate(session["memory"], 1):
        print(f"{i}. [{item['intent']}] {item['query']} → {item['response']}")

if __name__ == "__main__":
    main()
