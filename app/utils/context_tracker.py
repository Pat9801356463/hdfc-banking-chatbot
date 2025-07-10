# utils/context_tracker.py

def get_last_use_case(session):
    if "memory" in session and session["memory"]:
        return session["memory"][-1].get("use_case", None)
    return None

def update_context_with_memory(query, session):
    # If no strong use case is found, fallback to previous one
    from .intent_mapper import classify_intent_and_usecase
    
    classification = classify_intent_and_usecase(query)
    intent = classification.get("intent")
    use_case = classification.get("use_case")

    # If Gemini can't find use case and we have past memory
    if use_case == "Unclear" and get_last_use_case(session):
        use_case = get_last_use_case(session)

    return intent, use_case
