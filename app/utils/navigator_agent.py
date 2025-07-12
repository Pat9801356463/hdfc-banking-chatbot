# utils/navigator_agent.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_headless_browser():
    """
    Sets up a headless Chrome browser using Selenium with recommended options.
    
    Returns:
        webdriver.Chrome: A Selenium WebDriver instance.
    """
    options = Options()
    options.add_argument("--headless=new")  # For Chrome 109+
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def fetch_rendered_html(url, wait_time=5):
    """
    Uses Selenium to load a webpage and return fully rendered HTML.

    Args:
        url (str): The target webpage URL.
        wait_time (int): Delay (in seconds) to allow JS content to load.

    Returns:
        str: Rendered HTML content or an error string.
    """
    try:
        driver = setup_headless_browser()
        driver.get(url)
        time.sleep(wait_time)
        html = driver.page_source
        driver.quit()
        return html
    except Exception as e:
        print(f"[Navigator Error] fetch_rendered_html failed: {e}")
        return ""

def navigate_and_capture(url: str) -> str:
    """
    Adapter for agent_orchestrator to call rendered HTML extractor.

    Args:
        url (str): Web page to navigate.

    Returns:
        str: HTML content of the page.
    """
    print(f"[Navigator] Navigating to: {url}")
    return fetch_rendered_html(url)
