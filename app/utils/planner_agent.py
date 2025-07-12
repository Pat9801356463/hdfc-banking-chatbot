import os
from dotenv import load_dotenv
from utils.gemini_helper import safe_generate_content
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gemini = genai.GenerativeModel("gemini-1.5-flash")


def plan_tools_for_query(query: str) -> list:
    """
    Given a user query, return an ordered list of tools to use:
    ["search", "navigate", "scrape", "validate", "link_resolver", "none"]

    'none' means no external tools are required.
    """

    prompt = f"""
You are a planning agent in a banking assistant system.
Given the user query, select a logical sequence of tools that should be used.

Available tools:
- search: Perform a Google/SerpAPI search.
- navigate: Use Selenium to open dynamic pages.
- scrape: Extract structured data from HTML using BeautifulSoup.
- validate: Check if scraped data matches known schema.
- link_resolver: Use Gemini/Cohere to suggest a direct official link.
- none: No tools needed (use cached or local response only).

Only return tools in a Python list in correct order.

Examples:
Q: "What is the latest RBI repo rate?"
A: ["search", "scrape", "validate"]

Q: "How to block my HDFC credit card?"
A: ["link_resolver"]

Q: "What is form 16B download process?"
A: ["search", "scrape", "validate"]

Q: "List some credit cards from HDFC"
A: ["search", "scrape", "validate"]

Q: "Check my mutual fund tax benefits"
A: ["none"]

Now answer for:
"{query}"
"""
    try:
        response = safe_generate_content(gemini, prompt)
        tools = eval(response)  # Expecting something like ["search", "scrape"]
        if isinstance(tools, list):
            return tools
    except Exception as e:
        print(f"[Planner Error] {e}")

    return ["none"]  # Fallback if planner fails
