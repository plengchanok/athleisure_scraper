from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import os

try:
    # Setup Selenium with more realistic browser settings
    print("Setting up Chrome driver...")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")  # Use the newer headless mode
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en")
    # Add user agent to appear more like a real browser
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    # Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Execute CDP commands to prevent detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """
    })
    
    # Open the Athleta new arrivals page
    url = "https://athleta.gap.com/browse/new/all-new-arrivals?cid=1006482&mlink=1%2C1%2CMeganav_1&nav=meganav%3ANew%3A%3A"
    print(f"Opening URL: {url}")
    driver.get(url)
    
    # Wait for initial page load
    print("Waiting for page to load...")
    time.sleep(10)
    
    # Save the HTML page for debugging
    with open("athleta_debug_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved current HTML page to athleta_debug_page.html for debugging.")
    
    # Try to close any modals or popups
    try:
        print("Attempting to close modals and popups...")
        
        # Look for common close buttons
        close_button_xpaths = [
            "//button[contains(@class, 'close')]",
            "//div[contains(@class, 'modal')]//button",
            "//button[contains(text(), 'Close')]",
            "//button[contains(@aria-label, 'Close')]",
            "//button[contains(@aria-label, 'Dismiss this popup')]",
            "//button[@aria-label='Close']",
            "//span[@class='close-button']"
        ]
        
        for xpath in close_button_xpaths:
            try:
                close_buttons = driver.find_elements(By.XPATH, xpath)
                for button in close_buttons:
                    if button.is_displayed():
                        button.click()
                        print(f"Clicked a close button: {xpath}")
                        time.sleep(1)
            except Exception as e:
                continue

        # Try clicking outside the modal to close it
        try:
            ActionChains(driver).move_by_offset(10, 10).click().perform()
            print("Clicked outside the modal to close it.")
            # Move the mouse back to the center to avoid offset issues in future actions
            ActionChains(driver).move_by_offset(-10, -10).perform()
            time.sleep(1)
        except Exception as e:
            print(f"Failed to click outside the modal: {e}")
    
    except Exception as e:
        print(f"Failed to close modals: {e}")
    
    # Fix any scrolling issues
    print("Enabling scrolling...")
    driver.execute_script("""
        document.documentElement.style.overflow = 'auto';
        document.body.style.overflow = 'auto';
    """)
    
    # Scroll down to load all products
    print("Scrolling to load all products...")
    actions = ActionChains(driver)
    num_scrolls = 25
    wait_time = 2
    for i in range(num_scrolls):
        print(f"Scroll {i+1}/{num_scrolls}")
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(wait_time)
        try:
            actions.move_to_element(driver.find_element(By.TAG_NAME, 'body')).perform()
        except:
            print("Could not move to body element")
    
    # Now proceed with scraping the content
    print("Beginning to scrape product data...")
    
    # Extract product data from the page
    try:
        print("Extracting product data...")
        
        # Get the page source
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Find all product tiles
        product_tiles = soup.select('.product-card')
        print(f"Found {len(product_tiles)} product tiles")
        
        for tile in product_tiles:
            try:
                # Product Name
                name_element = tile.select_one('div.sitewide-w8zxc')
                name = name_element.text.strip() if name_element else "Unknown"

                # Product URL
                url_element = tile.select_one('a.sitewide-0')
                url = url_element.get("href") if url_element else "Unknown"
                if isinstance(url, str) and url.startswith("/"):
                    url = "https://athleta.gap.com" + url

                # Image URL
                img_element = tile.select_one('.cat_product-image img')
                image_url = img_element.get("src") if img_element else ""
                if isinstance(image_url, str) and image_url.startswith("/"):
                    image_url = "https://athleta.gap.com" + image_url

                # Price
                price_element = tile.select_one('.product-card-price span')
                price = price_element.text.strip() if price_element else "Unknown"
                
                # Create product dictionary
                product = {
                    'Index': len(products) + 1,
                    'Date': pd.Timestamp.today().strftime('%Y-%m-%d'),
                    'Brand': "athleta",
                    'Product Name': name,
                    'Price': price,
                    'URL': url,
                    'Image URL': image_url
                }
                products.append(product)
            except Exception as e:
                print(f"Error processing product tile: {e}")

        if products:
            # Create DataFrame
            df = pd.DataFrame(products)
            
            # Google Sheets integration
            creds_path = os.environ.get('CREDS_PATH', '/Users/pleng/python/pleng.io/spatial-framing-452703-g4-d9e7337e6b02.json')

            # Authenticate with Google Sheets
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
            client = gspread.authorize(creds)

            # Open the Google Sheet
            SHEET_ID = os.environ.get('SHEET_ID', "1G4cuYs_7qD1ft6OEhovLjj8zowQc92yYHQz2gSmLpp8")
            sheet_name = "athleta"
            
            # Try to open the worksheet, create it if it doesn't exist
            try:
                sheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)
            except:
                sheet = client.open_by_key(SHEET_ID).add_worksheet(title=sheet_name, rows=1000, cols=20)

            # Convert DataFrame to a list of lists for Google Sheets
            data_to_append = df.values.tolist()

            # Append new data
            sheet.append_rows(data_to_append)

            print("Data successfully uploaded to Google Sheets!")
        else:
            print("No product data found!")
            
    except Exception as e:
        print(f"Error in script: {e}")

finally:
    # Close the driver
    print("Closing browser...")
    if 'driver' in locals():
        driver.quit()