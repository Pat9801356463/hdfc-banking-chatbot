# utils/validator_agent.py
import re
import os

MIN_TEXT_LENGTH = 300
VALID_URL_PATTERN = re.compile(r"^https?://[\w./%-]+$")


# -------------------- Basic Validators --------------------

def is_valid_url(url: str) -> bool:
    return isinstance(url, str) and bool(VALID_URL_PATTERN.match(url.strip()))


def validate_links(links: list) -> list:
    valid = []
    for link in links:
        if isinstance(link, tuple) and len(link) == 2:
            title, url = link
            if title and is_valid_url(url):
                valid.append((title.strip(), url.strip()))
    return valid


def validate_text(text: str) -> bool:
    return isinstance(text, str) and len(text.strip()) >= MIN_TEXT_LENGTH


def validate_table_text(tables: str) -> bool:
    return isinstance(tables, str) and ("|" in tables or "\n" in tables)


def validate_scraped_data(scraped: dict) -> dict:
    valid_data = {}

    if "text" in scraped and validate_text(scraped["text"]):
        valid_data["text"] = scraped["text"]

    if "tables" in scraped and validate_table_text(scraped["tables"]):
        valid_data["tables"] = scraped["tables"]

    if "links" in scraped:
        links = validate_links(scraped["links"])
        if links:
            valid_data["links"] = links

    return valid_data


def is_valid_response(scraped: dict) -> bool:
    validated = validate_scraped_data(scraped)
    return bool(validated)


# -------------------- Use Case Schema Validation --------------------

def validate_schema_against_usecase(use_case: str, scraped: dict) -> bool:
    """
    Check if scraped data satisfies minimum schema based on use case.
    You can fine-tune expected schema per use case.
    """
    use_case = use_case.lower()

    if "kyc" in use_case or "documentation" in use_case:
        return "links" in scraped and len(scraped["links"]) > 0

    elif "interest" in use_case or "rates" in use_case:
        return "tables" in scraped or "text" in scraped

    elif "rbi" in use_case or "circulars" in use_case:
        return "links" in scraped

    elif "credit card" in use_case:
        return "text" in scraped or "links" in scraped

    elif "mutual fund" in use_case:
        return "tables" in scraped or "text" in scraped

    return is_valid_response(scraped)


# -------------------- Source Classification --------------------

def extract_metadata_type(scraped: dict) -> str:
    """
    Tags whether source is RBI or HDFC based on text/links.
    """
    text = scraped.get("text", "").lower()
    links = [url.lower() for _, url in scraped.get("links", [])]

    if "rbi.org.in" in text or any("rbi.org.in" in l for l in links):
        return "RBI"

    if "hdfcbank.com" in text or any("hdfcbank.com" in l for l in links):
        return "HDFC"

    return "Unknown"


# -------------------- Scrape Logging (Optional) --------------------

def log_invalid_payload(query: str, html: str, save_dir="logs/bad_scrapes"):
    """
    Dumps HTML of failed scrape for debugging.
    """
    os.makedirs(save_dir, exist_ok=True)
    file_name = re.sub(r'\W+', '_', query.lower())[:40]
    file_path = os.path.join(save_dir, f"{file_name}.html")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"<!-- Query: {query} -->\n\n")
            f.write(html)
        print(f"[🛠️ Debug] Saved bad scrape HTML to: {file_path}")
    except Exception as e:
        print(f"[⚠️ Logging Failed] {e}")
