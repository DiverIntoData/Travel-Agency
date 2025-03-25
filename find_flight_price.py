def find_flight_price(flight_origin, flight_destination, departure_date, return_date=None):
    import time
    import re
    import random
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium_stealth import stealth

    # Initialize price_number with a default value
    price_number = None

    # Set Chrome options for headless mode
    options = Options()
    options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")



    # Set a realistic user agent
    # user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
    # options.add_argument(f'user-agent={user_agent}')

    # Disable automation flags
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)

    # Use webdriver-manager to automatically manage ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Create new instance of Chrome in headless mode
    browser = webdriver.Chrome(service=service, options=options)

    stealth(
        browser,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True
        )

    # Modify navigator properties using JavaScript
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

    # Set a wide screen size
    browser.set_window_size(1920, 1080)

    # Determine if the trip is one-way or round trip, and use the proper URL
    if return_date is None:
        kayak_url = f"https://www.kayak.es/flights/{flight_origin}-{flight_destination}/{departure_date}?ucs=1993xcp"
    else:
        kayak_url = f"https://www.kayak.es/flights/{flight_origin}-{flight_destination}/{departure_date}/{return_date}?ucs=1993xcp"

    # Open the website
    browser.get(kayak_url)

    # Wait for the page to load
    time.sleep(random.uniform(10, 20))  # Random delay to mimic human behavior

    # Save a screenshot for debugging
    browser.save_screenshot('screenshot.png')

    # Print the page source for debugging
    print(browser.page_source)

    # Find all elements with the class name
    all_prices = browser.find_elements(By.CLASS_NAME, 'Hv20-value')

    # Check if there are at least two elements
    if len(all_prices) >= 2:
        # Get the second element
        second_price = all_prices[1].text
        price_number_match = re.search(r'\d+', second_price)
        if price_number_match:
            price_number = int(price_number_match.group())
        else:
            print('Number not found in "El Mejor".')
    else:
        print('There is no element "El mas barato" or "El Mejor".')

    # Close the browser
    browser.close()

    return price_number