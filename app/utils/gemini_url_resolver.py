# app/utils/gemini_url_resolver.py

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# -- Example Knowledge Base (optional fallback)
KNOWN_LINKS = {
    "kyc update": "https://instaservices.hdfcbank.com/?journey=116",
    "mobile update": "https://instaservices.hdfcbank.com/?journey=105",
    "email update": "https://instaservices.hdfcbank.com/?journey=106",
    "interest certificate": "https://xpressforms.hdfcbank.com/login?redirect=%2Fforms%2Fic01",
    "forms centre": "https://www.hdfcbank.com/personal/resources/forms-centre",
    "netbanking login": "https://netbanking.hdfcbank.com/netbanking/",
    "block card": "https://www.hdfcbank.com/personal/faq/card-blocking"
}

def extract_relevant_url_from_query(query: str) -> dict:
    prompt = f"""
You are an intelligent banking assistant for HDFC Bank.
The user asked: "{query}"

From your knowledge or official HDFC links, suggest the most relevant official URL to help the user.

Return your response in this format:
Title: <title>
URL: <official_url>

If no match is found, return:
Title: None
URL: None
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        lines = text.splitlines()
        result = {"title": None, "url": None}
        for line in lines:
            if line.lower().startswith("title:"):
                result["title"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("url:"):
                result["url"] = line.split(":", 1)[1].strip()
        return result
    except Exception as e:
        return {"title": "Error", "url": f"Gemini API error: {e}"}

def fallback_from_known_links(query: str) -> dict:
    for keyword, link in KNOWN_LINKS.items():
        if keyword in query.lower():
            return {"title": keyword.title(), "url": link}
    return {"title": None, "url": None}

def get_best_url_for_query(query: str) -> dict:
    result = extract_relevant_url_from_query(query)
    if not result["url"] or result["url"].lower() == "none":
        return fallback_from_known_links(query)
    return result

def format_url_response(data: dict) -> str:
    if data["title"] and data["url"]:
        return f"Here is the link for **{data['title']}**: [Click here]({data['url']})"
    return "❌ No relevant official link found. Please refine your question."

# --- Example usage ---
if __name__ == "__main__":
    q = input("Ask a query to find the relevant URL: ")
    url_data = get_best_url_for_query(q)
    print(format_url_response(url_data))
