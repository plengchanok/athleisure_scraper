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
    options.add_argument("--headless=new")  # Use the newer headless mode
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
    
    # Open the Beyond Yoga new arrivals page
    url = "https://beyondyoga.com/collections/new-arrivals"
    print(f"Opening URL: {url}")
    driver.get(url)
    
    # Wait for initial page load
    print("Waiting for page to load...")
    time.sleep(5)
    
    # Try to close any modals or popups
    try:
        print("Attempting to close modals and popups...")
        
        # Look for common close buttons
        close_button_xpaths = [
            "//button[contains(@class, 'close')]",
            "//div[contains(@class, 'modal')]//button",
            "//button[contains(text(), 'Close')]",
            "//button[contains(@aria-label, 'Close')]",
            "//button[@aria-label='Close dialog']"
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
    num_scrolls = 20
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
        product_tiles = soup.select('.product-item')
        print(f"Found {len(product_tiles)} product tiles")
        
        for tile in product_tiles:
            try:
                # Extract product name
                name_element = tile.select_one('.product-item__title')
                name = name_element.text.strip() if name_element else "Unknown"
                
                # Extract price
                price_element = tile.select_one('.product-item__price')
                price = price_element.text.strip() if price_element else "Unknown"
                
                # Extract product URL
                link_element = tile.select_one('a.product-item__link')
                url = "https://beyondyoga.com" + link_element.get("href") if link_element and link_element.get("href") else "Unknown"
                
                # Extract image URL
                img_element = tile.select_one('img.product-item__image')
                image_url = ""
                if img_element:
                    if img_element.get("src"):
                        image_url = img_element.get("src")
                    elif img_element.get("data-src"):
                        image_url = img_element.get("data-src")
                
                # Create product dictionary
                product = {
                    'Index': len(products) + 1,
                    'Date': pd.Timestamp.today().strftime('%Y-%m-%d'),
                    'Brand': "beyond yoga",
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
            sheet_name = "beyond_yoga"
            
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