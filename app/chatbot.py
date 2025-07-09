# app/chatbot.py

from utils.session_manager import load_user_session
from utils.intent_mapper import classify_intent_and_usecase
from utils.rag_engine import load_documents_for_use_case
from utils.response_generator import generate_final_answer

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

        # Step 1: Use Gemini to classify intent and use case
        classification = classify_intent_and_usecase(query)
        intent = classification["intent"]
        use_case = classification["use_case"]

        print(f"🧠 Intent: {intent}")
        print(f"📂 Use Case: {use_case}")

        # Step 2: Load context based on use case
        if use_case in [
            "Investment (non-sharemarket)",
            "Documentation & Process Query",
            "Loan Prepurchase Query",
            "Fraud Complaint - Scenario",
            "Banking Norms",
            "KYC & Details Update"
        ]:
            context = load_documents_for_use_case(use_case)

        elif use_case == "Transaction History":
            context = session["transactions"].tail(5).to_string(index=False)

        elif use_case == "Download Statement & Document":
            context = "You can download your documents here:\n" \
                      "- Account Statement: https://hdfcbank.com/download/statement\n" \
                      "- PAN Update Form: https://hdfcbank.com/update-pan"

        elif use_case == "Mutual Funds & Tax Benefits":
            context = "You have invested in ELSS and Tax Saver Mutual Funds. These are eligible for deductions under Section 80C."

        else:
            context = "❓ No predefined context found for this use case."

        # Step 3: Generate final response
        final_response = generate_final_answer(query, context, session["name"])

        # Step 4: Store interaction in session memory
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
