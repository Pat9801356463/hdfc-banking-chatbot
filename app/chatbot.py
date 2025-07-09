# app/chatbot.py
from utils.session_manager import load_user_session

def main():
    print("🟢 Welcome to the HDFC Banking Assistant\n")

    user_id = input("Enter your User ID (e.g. 001): ").strip()
    session, greeting = load_user_session(user_id)

    if session is None:
        print(greeting)
        return

    print(greeting)

    # CLI loop to simulate memory tracking
    while True:
        query = input("\n💬 Your Query (or type 'exit' to quit): ").strip()
        if query.lower() in ['exit', 'quit']:
            break

        # For now, echo back and store in memory (we’ll plug in LLM later)
        dummy_response = f"(Mock response to): {query}"

        session['memory'].append({
            "query": query,
            "response": dummy_response
        })

        print(f"🤖 {dummy_response}")

    # Print memory at end of session
    print("\n📝 Session Memory:")
    for i, mem in enumerate(session["memory"], 1):
        print(f"{i}. {mem['query']} → {mem['response']}")

if __name__ == "__main__":
    main()
