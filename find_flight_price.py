# find_flight_price.py

import time
import re
import random
# from selenium import webdriver  # Keep commented or remove
# from selenium.webdriver.common.by import By # Import By correctly
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service # Keep commented or remove
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager # Keep commented or remove
from selenium_stealth import stealth
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def find_flight_price(flight_origin, flight_destination, departure_date, return_date=None):
    price_number = None
    browser = None # Initialize browser to None for finally block

    try:
        options = Options() # Use uc.ChromeOptions() if Options() gives issues, but usually standard Options works
        # options = uc.ChromeOptions() # Alternative if needed

        options.add_argument("--headless")
        options.add_argument("--no-sandbox") # Essential in container environments
        options.add_argument("--disable-dev-shm-usage") # Essential in container environments
        options.add_argument('--disable-gpu') # Often needed for headless

        # *** THIS IS THE KEY FIX ***
        # Explicitly set the binary location for Chromium installed via packages.txt
        options.binary_location = '/usr/bin/chromium-browser'
        # If the above path doesn't work after deploying, try:
        # options.binary_location = '/usr/bin/chromium'

        # Create new instance of Chrome using undetected_chromedriver
        browser = uc.Chrome(options=options, use_subprocess=True)

        # Apply stealth settings
        stealth(
            browser,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Linux x86_64", # More appropriate for the Streamlit environment
            webgl_vendor="Intel Inc.", # You can keep these generic if unsure
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
        )

        # Modify navigator properties
        browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            },
        )

        # Set window size
        browser.set_window_size(1920, 1080)

        
        # Determine URL
        if return_date is None:
            kayak_url = f"https://www.kayak.es/flights/{flight_origin}-{flight_destination}/{departure_date}?ucs=1993xcp"
        else:
            kayak_url = f"https://www.kayak.es/flights/{flight_origin}-{flight_destination}/{departure_date}/{return_date}?ucs=1993xcp"

        # Open the website
        print(f"Attempting to get URL: {kayak_url}") # Add logging
        browser.get(kayak_url)
        print(f"Successfully got URL: {kayak_url}") # Add logging

        # --- Use Explicit Waits ---
        # Wait up to 30 seconds for the price elements (use a robust selector!)
        # Replace By.CLASS_NAME, 'Hv20-value' with a better selector found via DevTools
        # Example using a hypothetical robust selector:
        # wait = WebDriverWait(browser, 30)
        # price_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid='result-best'] span.price-value")))

        # Using your original selector for now, but replace it!
        wait = WebDriverWait(browser, 30) # Wait up to 30 seconds
        print("Waiting for price elements...") # Add logging
        # Ensure By is imported: from selenium.webdriver.common.by import By
        price_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Hv20-value')))
        print(f"Found {len(price_elements)} price elements.") # Add logging

        if len(price_elements) >= 2:
            second_price_text = price_elements[1].text
            print(f"Raw second price text: '{second_price_text}'") # Add logging
            # Improved regex to handle various currency/decimal formats: remove non-digits first
            cleaned_price = re.sub(r'[^\d]', '', second_price_text)
            if cleaned_price:
                price_number = int(cleaned_price)
                print(f"Extracted price: {price_number}") # Add logging
            else:
                print(f'Number not found in element text after cleaning: {second_price_text}')
                # browser.save_screenshot('debug_extraction_fail.png') # Won't work easily on Streamlit Cloud fs
        else:
            print('Less than two price elements found.')
            # browser.save_screenshot('debug_not_enough_elements.png')

    except TimeoutException:
        print("Timed out waiting for price elements to load.")
        # print(browser.page_source) # Print source for debugging
    except NoSuchElementException:
        print("Price element could not be found using the specified selector.")
        # print(browser.page_source)
    except Exception as e:
        print(f"An unexpected error occurred during scraping: {e}")
        # import traceback
        # print(traceback.format_exc()) # Print full traceback
        # if browser: print(browser.page_source)
    finally:
        # Ensure browser is closed even if errors occur
        if browser:
            print("Closing browser.") # Add logging
            browser.quit()

    return price_number
