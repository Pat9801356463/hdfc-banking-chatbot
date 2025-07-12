# utils/scraper_agent.py

from bs4 import BeautifulSoup

def extract_text_from_html(html: str) -> str:
    """
    Generic fallback: extracts all visible text content from the HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def extract_links(html: str, limit=5) -> list:
    """
    Extracts (title, URL) from <a> tags. Useful for circulars, forms, etc.
    """
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = a["href"]
        if text and href.startswith("http"):
            links.append((text, href))
        if len(links) >= limit:
            break
    return links

def extract_table_text(html: str) -> str:
    """
    Extracts and formats all tables into plain text.
    """
    soup = BeautifulSoup(html, "html.parser")
    output = []

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = row.find_all(["td", "th"])
            line = " | ".join(col.get_text(strip=True) for col in cols)
            if line:
                output.append(line)
        output.append("-" * 50)

    return "\n".join(output)

def smart_scrape(html: str) -> dict:
    """
    Combines all scraping methods and returns a structured dict.
    """
    return {
        "text": extract_text_from_html(html),
        "tables": extract_table_text(html),
        "links": extract_links(html),
    }

# --- Test block (optional) ---
if __name__ == "__main__":
    with open("sample_page.html", "r", encoding="utf-8") as f:
        html = f.read()

    result = smart_scrape(html)
    print("\n📄 Text:\n", result["text"][:500])
    print("\n📊 Tables:\n", result["tables"])
    print("\n🔗 Links:\n", result["links"])
