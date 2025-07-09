import os
import google.generativeai as genai

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load model
model = genai.GenerativeModel("gemini-1.5-flash")

# Final 9 use cases
USE_CASES = [
    "Investment (non-sharemarket)",
    "Documentation & Process Query",
    "Transaction History",
    "Download Statement & Document",
    "Loan Prepurchase Query",
    "Fraud Complaint - Scenario",
    "Mutual Funds & Tax Benefits",
    "Banking Norms",
    "KYC & Details Update"
]

def classify_intent_and_usecase(query):
    prompt = f"""
You are a helpful banking assistant. A user asked:
"{query}"

Identify:
1. The **intent** (short action: e.g., "check_status", "raise_dispute", "download_file")
2. The most relevant **use case** from this list:
{chr(10).join(["- " + uc for uc in USE_CASES])}

Return your answer in this format:
Intent: <short_intent>
Use Case: <selected_use_case>
"""

    try:
        response = model.generate_content(prompt)
        return parse_intent_usecase_response(response.text)
    except Exception as e:
        return {"intent": "unknown", "use_case": "unknown", "error": str(e)}

def parse_intent_usecase_response(response_text):
    lines = response_text.strip().splitlines()
    intent = use_case = None

    for line in lines:
        if line.lower().startswith("intent:"):
            intent = line.split(":", 1)[1].strip()
        elif line.lower().startswith("use case:"):
            use_case = line.split(":", 1)[1].strip()

    return {
        "intent": intent or "unknown",
        "use_case": use_case or "unknown"
    }
