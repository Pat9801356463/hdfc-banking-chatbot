import os
import requests
from dotenv import load_dotenv

load_dotenv()

# You can choose either SERPAPI or Google Custom Search
USE_SERPAPI = True  # Change to False if using Google Custom Search

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CSE_ID")

def search_web(query, num_results=5):
    """
    Perform a search using SerpAPI or Google CSE and return a list of (title, URL) tuples.
    """
    if USE_SERPAPI:
        return search_with_serpapi(query, num_results)
    else:
        return search_with_google_cse(query, num_results)


def search_with_serpapi(query, num_results=5):
    try:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": num_results,
            "engine": "google"
        }
        res = requests.get("https://serpapi.com/search", params=params, timeout=10)
        res.raise_for_status()
        results = res.json()

        links = []
        for item in results.get("organic_results", [])[:num_results]:
            title = item.get("title")
            link = item.get("link")
            if title and link:
                links.append((title, link))

        return links or [("⚠️ No results found", "")]
    except Exception as e:
        return [(f"⚠️ Search error: {e}", "")]


def search_with_google_cse(query, num_results=5):
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CX,
            "q": query,
            "num": num_results,
        }
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()

        links = []
        for item in data.get("items", []):
            title = item.get("title")
            link = item.get("link")
            if title and link:
                links.append((title, link))

        return links or [("⚠️ No results found", "")]
    except Exception as e:
        return [(f"⚠️ Google CSE error: {e}", "")]
