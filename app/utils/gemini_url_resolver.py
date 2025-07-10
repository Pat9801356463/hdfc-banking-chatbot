# app/utils/gemini_url_resolver.py

import os
from dotenv import load_dotenv
from utils.cohere_helper import safe_generate_cohere
from utils.gemini_helper import safe_generate_content
import google.generativeai as genai

# Load env vars
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Known links for fallback
KNOWN_LINKS = {
    "kyc update": "https://instaservices.hdfcbank.com/?journey=116",
    "mobile update": "https://instaservices.hdfcbank.com/?journey=105",
    "email update": "https://instaservices.hdfcbank.com/?journey=106",
    "interest certificate": "https://xpressforms.hdfcbank.com/login?redirect=%2Fforms%2Fic01",
    "forms centre": "https://www.hdfcbank.com/personal/resources/forms-centre",
    "netbanking login": "https://netbanking.hdfcbank.com/netbanking/",
    "block card": "https://www.hdfcbank.com/personal/faq/card-blocking"
}


def parse_title_url(response_text: str) -> dict:
    lines = response_text.strip().splitlines()
    result = {"title": None, "url": None}
    for line in lines:
        if line.lower().startswith("title:"):
            result["title"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("url:"):
            result["url"] = line.split(":", 1)[1].strip()
    return result


def extract_url_using_cohere(query: str) -> dict:
    prompt = f"""
You are an intelligent assistant for HDFC Bank.

The user asked: "{query}"

Return the best official HDFC-related URL if possible.

Use this format:
Title: <title>
URL: <url>
"""
    response_text = safe_generate_cohere(prompt)
    return parse_title_url(response_text)


def extract_url_using_gemini(query: str) -> dict:
    prompt = f"""
You are an intelligent assistant for HDFC Bank.

The user asked: "{query}"

Return the best official HDFC-related URL if possible.

Use this format:
Title: <title>
URL: <url>
"""
    response_text = safe_generate_content(gemini_model, prompt)
    return parse_title_url(response_text)


def fallback_from_known_links(query: str) -> dict:
    for keyword, link in KNOWN_LINKS.items():
        if keyword in query.lower():
            return {"title": keyword.title(), "url": link}
    return {"title": None, "url": None}


def get_best_url_for_query(query: str) -> dict:
    # 1. Try Cohere first
    result = extract_url_using_cohere(query)
    if result["url"] and result["url"].startswith("http"):
        return result

    # 2. Fallback to Gemini
    result = extract_url_using_gemini(query)
    if result["url"] and result["url"].startswith("http"):
        return result

    # 3. Fallback to static list
    return fallback_from_known_links(query)


def format_url_response(data: dict) -> str:
    if data["title"] and data["url"] and data["url"].startswith("http"):
        return f"Here is the link for **{data['title']}**: [Click here]({data['url']})"
    return "❌ No relevant official link found. Please refine your question."


def resolve_link_via_gemini(query: str) -> str:
    return format_url_response(get_best_url_for_query(query))


# --- Test run
if __name__ == "__main__":
    q = input("Ask something: ")
    print(resolve_link_via_gemini(q))
