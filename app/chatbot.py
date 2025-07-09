# app/chatbot.py

from utils.session_manager import load_user_session
from utils.intent_mapper import classify_intent_and_usecase
from utils.rag_engine import load_documents_for_use_case

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

        # Step 2: Retrieve documents for the use case (RAG layer)
        context = load_documents_for_use_case(use_case)
        print("📄 Retrieved Context (trimmed):\n")
        print(context[:500])  # Preview first 500 characters

        # Step 3: Placeholder response (to be replaced with Gemini final generation)
        dummy_response = f"(Mock response based on context for use case '{use_case}')"

        # Step 4: Store everything in memory
        session["memory"].append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": context[:500],
            "response": dummy_response
        })

        # Final output
        print(f"🤖 {dummy_response}")

    # End of session summary
    print("\n📝 Session Memory Summary:")
    for i, item in enumerate(session["memory"], 1):
        print(f"{i}. [{item['intent']}] {item['query']} → {item['response']}")

if __name__ == "__main__":
    main()
