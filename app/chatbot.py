# app/chatbot.py

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
from utils.cohere_helper import classify_intent_usecase_cohere  # ⬅️ Cohere-based classifier
import pandas as pd

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

        # Step 1: Intent + Use Case classification using Cohere
        classification = classify_intent_usecase_cohere(query)
        intent = classification.get("intent", "unknown")
        use_case = classification.get("use_case", "unknown")
        session["memory"].append({"query": query, "intent": intent, "use_case": use_case})

        print(f"🧠 Intent: {intent}")
        print(f"📂 Use Case: {use_case}")

        # Step 2: Context resolution
        try:
            context = None

            # Try RAG first
            context = load_documents_for_use_case(use_case)
            if "⚠️" in context or len(context.strip()) < 20:
                raise ValueError("RAG context too weak")

        except Exception:
            # Step 2b: fallback to WebRetriever
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
                    if isinstance(cards, list) and len(cards) == 1 and cards[0].startswith("http"):
                        context = f"🔗 Please refer to the official credit card page: {cards[0]}"
                    else:
                        context = f"HDFC Bank offers the following credit cards:\n{format_credit_cards(cards)}"

                elif "interest rate" in query.lower():
                    rates = get_rbi_interest_rates()
                    if any("http" in v for v in rates.values()):
                        context = f"🔗 You can check RBI interest rates at: {list(rates.values())[0]}"
                    else:
                        context = f"Latest RBI Interest Rates:\n{format_interest_rates(rates)}"

                else:
                    link_response = resolve_link_via_gemini(query)
                    if link_response.startswith("http"):
                        context = f"🔗 Please refer to the following resource: {link_response}"
                    else:
                        context = f"{link_response}\n\nIf this doesn't answer your question, please clarify further."

            except Exception as e:
                context = f"⚠️ Failed to fetch relevant context due to: {e}"

        # Step 3: Generate answer via Gemini
        final_response = generate_final_answer(query, context, session["name"])

        # Step 4: Log memory with response
        session["memory"][-1].update({
            "context": context[:500],
            "response": final_response
        })

        print(f"\n🤖 {final_response}")

    # End summary
    print("\n🗒️ Session Summary:")
    for i, item in enumerate(session["memory"], 1):
        print(f"{i}. [{item['intent']}] {item['query']} → {item['response']}")

if __name__ == "__main__":
    main()
