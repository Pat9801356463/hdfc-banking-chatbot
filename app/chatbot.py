# app/chatbot.py (updated with agent orchestration)

from utils.session_manager import load_user_session
from utils.context_tracker import update_context_with_memory
from utils.response_generator import generate_final_answer
from utils.cache_manager import GlobalCache, is_public_query
from agents.agent_orchestrator import plan_and_execute_web_retrieval
import pandas as pd

def main():
    print("\U0001F7E2 Welcome to the HDFC Banking Assistant\n")

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

        # Step 1: Intent + Use Case
        intent, use_case = update_context_with_memory(query, session)
        print(f"\U0001F9E0 Intent: {intent}")
        print(f"📂 Use Case: {use_case}")

        # Step 2: Global Cache Check
        cached = None
        if is_public_query(intent, use_case):
            cached = GlobalCache.get(query)
            if cached:
                print("⚡ Response served from cache!")
                print(f"\n🤖 {cached}\n")
                continue

        # Step 3: Try RAG
        try:
            from utils.rag_engine import load_documents_for_use_case
            context = load_documents_for_use_case(use_case)
            if "⚠️" in context or len(context.strip()) < 50:
                raise ValueError("Weak or irrelevant RAG context")
        except:
            # Step 4: Agent Orchestration
            context = plan_and_execute_web_retrieval(query, use_case)

        # Step 5: Generate final answer
        final_response = generate_final_answer(query, context, session["name"])

        # Step 6: Store in memory
        session["memory"].append({
            "query": query,
            "intent": intent,
            "use_case": use_case,
            "context": context[:500],
            "response": final_response
        })

        print(f"\n🤖 {final_response}\n")

    # Wrap-up summary
    print("\n🗒️ Session Summary:")
    for i, item in enumerate(session["memory"], 1):
        print(f"{i}. [{item['intent']}] {item['query']} → {item['response'][:60]}...")

if __name__ == "__main__":
    main()
