# %%
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import os

try:
    # Setup Selenium
    print("Setting up Chrome driver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
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
    
    # Open the Alo Yoga bestsellers page
    url = "https://www.aloyoga.com/collections/bestsellers"
    print(f"Opening URL: {url}")
    driver.get(url)
    
    # Wait for page to load
    print("Waiting for page to load...")
    time.sleep(5)
    
    # Step 1: Remove the iframe if present
    try:
        iframe = driver.find_element(By.ID, "attentive_creative")  # Find the iframe
        driver.execute_script("arguments[0].remove();", iframe)  # Remove iframe using JavaScript
        print("Iframe removed successfully.")
        time.sleep(2)  # Wait for iframe to disappear
    except Exception as e:
        print("No blocking iframe detected:", e)
    
    # Step 2: Now, close the pop-up if present
    try:
        pop_up = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "osano-cm-dialog"))
        )
        # Click outside the popup by clicking on the body
        actions = ActionChains(driver)
        actions.move_by_offset(0, 0).click().perform()  # Click at current position
        print("Clicked outside popup to close it.")
        time.sleep(2)
    
    except Exception as e:
        print("No pop-up detected or issue closing it:", e)
    
    # Refresh the page to ensure clean state
    print("Refreshing page to ensure clean state...")
    driver.refresh()
    time.sleep(2)  # Wait for page to load after refresh
    
    # Fix scrolling issue
    print("Enabling scrolling...")
    driver.execute_script("document.documentElement.style.overflow = 'auto';")
    time.sleep(2)  # Wait for the page to stabilize after popup
    
    # Scroll down to load all products
    print("Scrolling to load all products...")
    actions = ActionChains(driver)
    num_scrolls = 20
    wait_time = 3  # Increased wait time between scrolls
    
    # First scroll to ensure we're at the top
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(2)
    
    for i in range(num_scrolls):
        print(f"Scroll {i+1}/{num_scrolls}")
        # Use JavaScript to scroll
        driver.execute_script(f"window.scrollTo(0, {(i+1) * 800});")  # Scroll by fixed amount
        time.sleep(wait_time)
        
        # Check if we've reached the bottom
        scroll_height = driver.execute_script("return document.documentElement.scrollHeight")
        current_position = driver.execute_script("return window.pageYOffset")
        if current_position >= scroll_height - 1000:  # If we're near the bottom
            print("Reached bottom of page")
            break
    
    # Final scroll to bottom to ensure everything is loaded
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(3)  # Wait for final load
    
    # Get the page source after interactions
    print("Extracting product data...")
    page_source = driver.page_source
    
    # # Save HTML for debugging
    # debug_file = "alo_debug.html"
    # print(f"Saving HTML content to {debug_file} for debugging...")
    # with open(debug_file, "w", encoding="utf-8") as f:
    #     f.write(page_source)
    # print(f"HTML content saved to {debug_file}")
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
        
    # Initialize lists to store product information
    product_names = []
    product_prices = []
    product_urls = []
    product_images = []
    
    # Find all product items using the correct class from the HTML
    product_items = soup.select('.PlpTile')
    
    print(f"Found {len(product_items)} product items")
    
    # Extract product information
    for item in product_items:
        # Extract product name - using the correct selectors from the HTML
        name_elem = item.select_one('.product-name a')
        if name_elem:
            name = name_elem.text.strip()
            product_names.append(name)
        else:
            product_names.append("Name not found")
        
        # Extract product price - using the correct selectors from the HTML
        price_elem = item.select_one('.card-price .product-price')
        if price_elem:
            price = price_elem.text.strip()
            product_prices.append(price)
        else:
            product_prices.append("Price not found")
        
        # Extract product URL - using the correct selectors from the HTML
        url_elem = item.select_one('.product-name a') or item.select_one('a')
        if url_elem and 'href' in url_elem.attrs:
            product_url = url_elem['href']
            if not product_url.startswith('http'):
                product_url = 'https://www.aloyoga.com' + product_url
            product_urls.append(product_url)
        else:
            product_urls.append("URL not found")
        
        # Extract product image - using multiple possible selectors
        img_elem = (
            item.select_one('.product-carousel img.normal') or
            item.select_one('.quick-add-carousel-images img') or
            item.select_one('img[class*="normal"]') or
            item.select_one('img[src*="cdn.shopify.com"]')
        )
    
        if img_elem and 'src' in img_elem.attrs:
            img_url = img_elem['src']
            product_images.append(img_url)
        else:
            product_images.append("Image not found")
    
    # Create a DataFrame with the extracted information
    df = pd.DataFrame({
        'Index': range(1, len(product_names) + 1),
        'Date': [pd.Timestamp.today().strftime('%Y-%m-%d')] * len(product_names),
        'Brand': ['alo yoga'] * len(product_names),
        'Product Name': product_names,
        'Price': product_prices,
        'URL': product_urls,
        'Image URL': product_images
    })
    
    # Google Sheets integration
    creds_path = os.environ.get('CREDS_PATH', '/Users/pleng/python/pleng.io/spatial-framing-452703-g4-d9e7337e6b02.json')
    
    # Authenticate with Google Sheets
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(creds)
    
    # Open the Google Sheet
    SHEET_ID = os.environ.get('SHEET_ID', "1G4cuYs_7qD1ft6OEhovLjj8zowQc92yYHQz2gSmLpp8")
    sheet_name = "alo"
    
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

except Exception as e:
    print(f"Error in script: {e}")

finally:
    # Close browser
    print("Closing browser...")
    if 'driver' in locals():
        driver.quit()

# %%



