from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def setup_headless_browser():
    """
    Sets up a headless Chrome browser with Selenium.
    """
    options = Options()
    options.add_argument("--headless=new")  # Chrome 109+
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_rendered_html(url, wait_time=5):
    """
    Uses Selenium to open a URL and return fully rendered HTML content.

    Args:
        url (str): The webpage URL.
        wait_time (int): Time (in seconds) to wait for page to load.

    Returns:
        str: The full HTML of the rendered page.
    """
    try:
        driver = setup_headless_browser()
        driver.get(url)
        time.sleep(wait_time)  # Wait for JS to render
        html = driver.page_source
        driver.quit()
        return html
    except Exception as e:
        return f"⚠️ Selenium navigation failed: {e}"
