# app/chatbot.py

from utils.session_manager import load_user_session
from utils.context_tracker import update_context_with_memory
from utils.rag_engine import load_documents_for_use_case
from utils.response_generator import generate_final_answer
import pandas as pd  # Needed for fraud ticket date

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

        # Step 1: Use Gemini to classify intent and infer use case (with memory fallback)
        intent, use_case = update_context_with_memory(query, session)

        print(f"🧠 Intent: {intent}")
        print(f"📂 Use Case: {use_case}")

        # Step 2: Load context for this use case
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

        # Step 3: Generate final response
        final_response = generate_final_answer(query, context, session["name"])

        # Step 4: Store interaction in memory
        session["memory"].append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": context[:500],
            "response": final_response
        })

        # Final output
        print(f"\n🤖 {final_response}")

    # End of session
    print("\n📝 Session Summary:")
    for i, item in enumerate(session["memory"], 1):
        print(f"{i}. [{item['intent']}] {item['query']} → {item['response']}")

if __name__ == "__main__":
    main()
