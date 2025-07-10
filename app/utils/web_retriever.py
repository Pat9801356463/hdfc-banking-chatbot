
# app/utils/web_retriever.py

import requests
from bs4 import BeautifulSoup

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

def get_hdfc_credit_cards(limit=5):
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

def get_rbi_interest_rates():
    url = "https://www.rbi.org.in/home.aspx"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
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

def format_circulars(circulars):
    return "\n".join([f"- {title}: {url}" for title, url in circulars])

def format_credit_cards(cards):
    return "\n".join([f"- {name}" for name in cards])

def format_interest_rates(rates):
    return "\n".join([f"- {k}: {v}" for k, v in rates.items()])
