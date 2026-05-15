import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Target URL that relies on JavaScript for content rendering
JS_HEAVY_URL = "http://quotes.toscrape.com/js/"
# A static URL for comparison (content available directly in HTML)
STATIC_URL = "http://quotes.toscrape.com/"

def fetch_with_requests(url):
    """Fetches content using the requests library (simple HTTP client)."""
    print(f"\n--- Fetching {url} with requests (simple HTTP client) ---")
    try:
        # Simulate a common web agent request with a standard User-Agent
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        print(f"Status Code: {response.status_code}")
        
        # --- ARTICLE CONCEPT ILLUSTRATION START ---
        # For JS-heavy sites, 'requests' only gets the initial HTML, not content loaded by JavaScript.
        # The target site 'quotes.toscrape.com/js/' initially shows 'Loading...' before JS populates quotes.
        if 'Loading...' in response.text:
            print("Content is likely incomplete (JS not executed). Found 'Loading...' placeholder.")
        else:
            print("Content seems complete or different from expected JS-loaded content.")
        # --- ARTICLE CONCEPT ILLUSTRATION END ---

        print("First 500 characters of response:")
        print(response.text[:500])
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching with requests: {e}")
        return None

def fetch_with_selenium(url):
    """Fetches content using Selenium with a headless browser (executes JavaScript)."""
    print(f"\n--- Fetching {url} with Selenium (headless browser) ---")
    
    # Setup Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu") # Recommended for headless on some systems
    chrome_options.add_argument("--no-sandbox") # Required for some environments
    chrome_options.add_argument("--window-size=1920,1080") # Set a consistent window size
    # Add a User-Agent to mimic a real browser, similar to the requests example
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    try:
        # Use webdriver_manager to automatically download and manage the ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        
        # Give the page some time to load and execute JavaScript
        time.sleep(3) # Adjust as needed based on page complexity and network speed

        # Get the page source after JS execution
        page_source = driver.page_source
        print(f"Page title: {driver.title}")
        print("First 500 characters of page source after JS execution:")
        print(page_source[:500])
        
        # --- ARTICLE CONCEPT ILLUSTRATION START ---
        # Selenium, by executing JavaScript, should retrieve the actual quotes, not the 'Loading...' placeholder.
        if 'Loading...' not in page_source and '<div class="quote">' in page_source:
            print("Content loaded successfully (JS executed). Found actual quotes.")
        else:
            print("Content might still be incomplete or JS did not execute as expected.")
        # --- ARTICLE CONCEPT ILLUSTRATION END ---

        return page_source
    except Exception as e:
        print(f"Error fetching with Selenium: {e}")
        return None
    finally:
        if driver:
            driver.quit() # Always close the browser

if __name__ == "__main__":
    print("This example demonstrates how web agents can fail on JavaScript-heavy sites and how a headless browser can solve it.")

    # 1. Demonstrate fetching a static page (both methods should work for comparison)
    print("\n--- Demonstrating with a STATIC page (both should work) ---")
    static_requests_content = fetch_with_requests(STATIC_URL)
    # For brevity, we'll skip Selenium for the static page, as its benefit is on JS-heavy sites.

    # 2. Demonstrate fetching a JavaScript-heavy page (requests fails, selenium succeeds)
    print("\n--- Demonstrating with a JAVASCRIPT-HEAVY page (requests fails, selenium succeeds) ---")
    js_requests_content = fetch_with_requests(JS_HEAVY_URL)
    js_selenium_content = fetch_with_selenium(JS_HEAVY_URL)

    # Simple comparison of results
    print("\n--- Comparison of results for JavaScript-heavy page ---")
    print(f"Requests output contains 'Loading...': {'Loading...' in str(js_requests_content)}")
    print(f"Selenium output contains actual quote structure ('<div class=\"quote\">'): {'<div class=\"quote\">' in str(js_selenium_content)}")
    print("\nAs seen, 'requests' only gets the initial HTML with a 'Loading...' placeholder, while 'Selenium' successfully renders the page and retrieves the full content after JavaScript execution.")
