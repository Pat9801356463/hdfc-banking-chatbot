# utils/web_retriever.py

import requests
from bs4 import BeautifulSoup
from utils.gemini_url_resolver import resolve_link_via_gemini  # Cohere-first now
from utils.scraper_agent import smart_scrape  # Required for run_scraper


# 📄 Get latest RBI circulars
def get_rbi_latest_circulars(limit=5):
    url = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        circulars = []
        for link in soup.select(".pressrelease li a")[:limit]:
            title = link.get_text(strip=True)
            href = link.get("href")
            full_url = f"https://www.rbi.org.in{href}"
            circulars.append((title, full_url))

        return circulars
    except Exception as e:
        return [("⚠️ Failed to retrieve RBI circulars", str(e))]


# 💳 Get HDFC credit card names or link
def get_hdfc_credit_cards(limit=5):
    try:
        resolved = resolve_link_via_gemini("List HDFC credit cards")
        if "http" in resolved:
            return [resolved]
    except Exception as e:
        print(f"Link resolution error: {e}")

    # Fallback: scrape cards list
    url = "https://www.hdfcbank.com/personal/pay/cards/credit-cards"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        cards = []
        for card_div in soup.select(".card-name")[:limit]:
            name = card_div.get_text(strip=True)
            cards.append(name)

        if not cards:
            cards.append("⚠️ Could not find card names. Structure might have changed.")

        return cards
    except Exception as e:
        return [f"⚠️ Failed to retrieve HDFC credit cards: {e}"]


# 📈 Get RBI interest rates or fallback link
def get_rbi_interest_rates():
    try:
        resolved = resolve_link_via_gemini("RBI interest rate table")
        if "http" in resolved:
            return {"🔗 RBI Rates Link": resolved}
    except Exception as e:
        print(f"Link resolution error: {e}")

    # Fallback: try to extract from homepage
    url = "https://www.rbi.org.in/home.aspx"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        rates = {}
        for row in soup.select(".rr_data tr"):
            cols = row.find_all("td")
            if len(cols) >= 2:
                label = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                rates[label] = value

        return rates if rates else {"⚠️": "No rates found. RBI homepage structure may have changed."}
    except Exception as e:
        return {"⚠️ Error": str(e)}


# 🧾 Formatting functions
def format_circulars(circulars):
    return "\n".join([f"- [{title}]({url})" for title, url in circulars])


def format_credit_cards(cards):
    return "\n".join([f"- {name}" for name in cards])


def format_interest_rates(rates):
    return "\n".join([f"- {k}: {v}" for k, v in rates.items()])


# 🔁 Scraper bridge for orchestrator
def run_scraper(html: str) -> dict:
    """
    Wrapper for smart_scrape to be used in orchestrator.
    """
    try:
        return smart_scrape(html)
    except Exception as e:
        return {"error": f"⚠️ Scraper failed: {e}"}
