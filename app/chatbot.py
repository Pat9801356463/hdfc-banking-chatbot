# app/chatbot.py

from utils.session_manager import load_user_session
from utils.intent_mapper import classify_intent_and_usecase

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

        # 👉 Step: Intent recognition via Gemini
        classification = classify_intent_and_usecase(query)
        intent = classification["intent"]
        use_case = classification["use_case"]

        # Placeholder response (we'll update this later with real logic)
        dummy_response = f"(Mock response to): {query}"

        # 🧠 Store everything in memory
        session["memory"].append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "response": dummy_response
        })

        # Output
        print(f"🧠 Intent: {intent}")
        print(f"📂 Use Case: {use_case}")
        print(f"🤖 {dummy_response}")

    # Optional: Summary of session
    print("\n📝 Session Summary:")
    for i, item in enumerate(session["memory"], 1):
        print(f"{i}. [{item['intent']}] {item['query']} → {item['response']}")

if __name__ == "__main__":
    main()

