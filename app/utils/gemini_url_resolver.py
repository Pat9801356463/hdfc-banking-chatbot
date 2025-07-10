# app/utils/gemini_url_resolver.py

import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Optional fallback links (static)
KNOWN_LINKS = {
    "kyc update": "https://instaservices.hdfcbank.com/?journey=116",
    "mobile update": "https://instaservices.hdfcbank.com/?journey=105",
    "email update": "https://instaservices.hdfcbank.com/?journey=106",
    "interest certificate": "https://xpressforms.hdfcbank.com/login?redirect=%2Fforms%2Fic01",
    "forms centre": "https://www.hdfcbank.com/personal/resources/forms-centre",
    "netbanking login": "https://netbanking.hdfcbank.com/netbanking/",
    "block card": "https://www.hdfcbank.com/personal/faq/card-blocking"
}


def extract_relevant_url_from_query(query: str, retries: int = 3, delay: float = 2.0) -> dict:
    prompt = f"""
You are an intelligent assistant for HDFC Bank.

The user asked: "{query}"

Return the best official HDFC-related URL, if possible.

Format:
Title: <title>
URL: <url>
"""
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            result = {"title": None, "url": None}
            for line in text.splitlines():
                if line.lower().startswith("title:"):
                    result["title"] = line.split(":", 1)[1].strip()
                elif line.lower().startswith("url:"):
                    result["url"] = line.split(":", 1)[1].strip()
            return result
        except Exception as e:
            # Retry on transient or quota errors
            if "429" in str(e) or "503" in str(e):
                time.sleep(delay * (attempt + 1))
                continue
            return {"title": "Error", "url": f"Gemini API error: {e}"}
    return {"title": "Error", "url": "Gemini API failed after retries."}


def fallback_from_known_links(query: str) -> dict:
    for keyword, link in KNOWN_LINKS.items():
        if keyword in query.lower():
            return {"title": keyword.title(), "url": link}
    return {"title": None, "url": None}


def get_best_url_for_query(query: str) -> dict:
    gemini_result = extract_relevant_url_from_query(query)
    if not gemini_result["url"] or gemini_result["url"].lower() == "none":
        return fallback_from_known_links(query)
    return gemini_result


def format_url_response(data: dict) -> str:
    if data["title"] and data["url"] and data["url"].startswith("http"):
        return f"Here is the link for **{data['title']}**: [Click here]({data['url']})"
    return "❌ No relevant official link found. Please refine your question."


# Handy alias
def resolve_link_via_gemini(query: str) -> str:
    return format_url_response(get_best_url_for_query(query))


# Test
if __name__ == "__main__":
    q = input("Ask something: ")
    print(resolve_link_via_gemini(q))
