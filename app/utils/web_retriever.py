# ✅ Enhanced web_retriever.py (integrated with gemini_url_resolver)
# app/utils/web_retriever.py

import requests
from bs4 import BeautifulSoup
from utils.gemini_url_resolver import get_best_url_for_query, format_url_response

# ========================= 🔗 Static Link Extracts from Uploaded Docs =========================

def get_hdfc_forms_links():
    return {
        "Main Portal": "https://www.hdfcbank.com/",
        "NetBanking Login": "https://netbanking.hdfcbank.com/netbanking/",
        "Forms Centre": "https://www.hdfcbank.com/personal/resources/forms-centre",
        "Insta Services": "https://www.hdfcbank.com/personal/resources/ways-to-bank/online-banking/insta-services",
        "Interest Certificate": "https://xpressforms.hdfcbank.com/login?redirect=%2Fforms%2Fic01",
    }

def get_kyc_update_links():
    return {
        "KYC Update Portal": "https://instaservices.hdfcbank.com/?journey=116",
        "Mobile Update Form (PDF)": "https://www.hdfcbank.com/content/dam/hdfc-aem-document/HDFC_Bank/forms/account-details-update/mobile-no-update-form.pdf",
        "Email Update Form (PDF)": "https://www.hdfcbank.com/content/dam/hdfc-aem-document/HDFC_Bank/forms/account-details-update/email-id-update-form.pdf",
        "Email Update Journey": "https://instaservices.hdfcbank.com/?journey=106",
        "Mobile Update Journey": "https://instaservices.hdfcbank.com/?journey=105"
    }

def get_fraud_reporting_info():
    return {
        "Block Debit/Credit Card": "https://www.hdfcbank.com/personal/faq/card-blocking",
        "Cyber Cell Email": "mailto:cybercell@payzapp.in",
        "Prepaid Card Support": "https://www.hdfcbank.com/personal/ways-to-bank/phone-banking",
        "PayZapp Contact": "https://www.hdfcbank.com/personal/make-payments/payzapp"
    }

def format_links_dict(data):
    return "\n".join([f"- [{k}]({v})" for k, v in data.items()])

# ========================= 🌐 Live Web Scraping =========================

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

# ========================= 📄 Formatters =========================

def format_circulars(circulars):
    return "\n".join([f"- {title}: {url}" for title, url in circulars])

def format_credit_cards(cards):
    return "\n".join([f"- {name}" for name in cards])

def format_interest_rates(rates):
    return "\n".join([f"- {k}: {v}" for k, v in rates.items()])

# ========================= 🤖 Gemini URL Resolver Integration =========================

def resolve_link_via_gemini(query: str) -> str:
    """Resolve dynamic URL suggestions from Gemini."""
    gemini_result = get_best_url_for_query(query)
    return format_url_response(gemini_result)
