# utils/validator_agent.py

import re

MIN_TEXT_LENGTH = 300  # minimum chars to be considered informative
VALID_URL_PATTERN = re.compile(r"^https?://[\w./%-]+$")

def is_valid_url(url: str) -> bool:
    """
    Checks whether the string is a valid URL.
    """
    return isinstance(url, str) and bool(VALID_URL_PATTERN.match(url.strip()))

def validate_links(links: list) -> list:
    """
    Ensures each link tuple has valid structure: (title, url)
    """
    valid = []
    for link in links:
        if isinstance(link, tuple) and len(link) == 2:
            title, url = link
            if title and is_valid_url(url):
                valid.append((title.strip(), url.strip()))
    return valid

def validate_text(text: str) -> bool:
    """
    Returns True if text has enough meaningful content.
    """
    return isinstance(text, str) and len(text.strip()) >= MIN_TEXT_LENGTH

def validate_table_text(tables: str) -> bool:
    """
    Very basic check for table structure: presence of delimiters or row patterns.
    """
    return isinstance(tables, str) and ("|" in tables or "\n" in tables)

def validate_scraped_data(scraped: dict) -> dict:
    """
    Given the `smart_scrape` result from `scraper_agent.py`, returns
    a validated and cleaned version. Empty sections are removed.
    """
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
    """
    Final check before caching or using scraped response.
    Returns True if at least one valid section exists.
    """
    validated = validate_scraped_data(scraped)
    return bool(validated)

# --- Optional test block
if __name__ == "__main__":
    test = {
        "text": "Short text.",
        "tables": "Label | Value\n---- | ----\nA | B",
        "links": [("RBI Circular", "https://rbi.org.in/link")]
    }
    print("✅ Validated:", validate_scraped_data(test))
    print("✔️ Is valid response?", is_valid_response(test))
