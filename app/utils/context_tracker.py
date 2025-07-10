# utils/context_tracker.py

from .intent_mapper import classify_intent_and_usecase

def get_last_use_case(session):
    """
    Retrieve the most recent use case from session memory.
    """
    if "memory" in session and session["memory"]:
        return session["memory"][-1].get("use_case", None)
    return None


def update_context_with_memory(query, session):
    """
    Classifies the user's query using Cohere.
    Falls back to the last known use case if classification is unclear.
    """
    classification = classify_intent_and_usecase(query)
    intent = classification.get("intent")
    use_case = classification.get("use_case")

    if use_case in ["unknown", "Unclear", None] and get_last_use_case(session):
        use_case = get_last_use_case(session)

    return intent, use_case
