# %%
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
import re
import gspread
from google.oauth2.service_account import Credentials
import os

try:
    # Setup Selenium
    print("Setting up Chrome driver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Open the Lululemon product page
    url = "https://shop.lululemon.com/c/women-bestsellers/n16o10znskl"
    print(f"Opening URL: {url}")
    driver.get(url)
    
    # Wait for initial page load
    print("Waiting for page to load...")
    time.sleep(5)
    
    # Close the newsletter modal (15% off popup)
    try:
        print("Attempting to close the newsletter modal...")
        
        # Click outside the modal (overlay click to dismiss)
        try:
            modal_wrapper = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "lululemon_mwa_promotions__modalWrapper__c3Tt0V"))
            )
            # Click outside the modal
            action = ActionChains(driver)
            action.move_by_offset(5, 5).click().perform()
            print("Tried clicking outside the modal")
            time.sleep(1)
        except Exception as e:
            print(f"Overlay click approach failed: {e}")
    
    except Exception as e:
        print(f"Failed to close the newsletter modal: {e}")
    
    # Fix any scrolling issues
    print("Enabling scrolling...")
    driver.execute_script("""
        document.documentElement.style.overflow = 'auto';
        document.body.style.overflow = 'auto';
    """)
    
    # Scroll down to load all products
    print("Scrolling to load all products...")
    actions = ActionChains(driver)
    num_scrolls = 12
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
    
    # Save the page for debugging
    with open("debug_page_lululemon.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved HTML to debug_page_lululemon.html for inspection.")
    
    # Extract product data from the page
    try:
        print("Extracting product data...")
        
        # Get the page source
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Find all product tiles
        product_tiles = soup.find_all("div", class_="product-tile")
        print(f"Found {len(product_tiles)} product tiles")
        
        for tile in product_tiles:
            try:
                # Extract product name
                name_element = tile.find("h3", class_="product-tile__product-name")
                name = name_element.text.strip() if name_element else "Unknown"
                
                # Extract price
                price_element = tile.find("span", class_="price")
                price = price_element.text.strip() if price_element else "Unknown"
                
                # Extract product URL
                link_element = tile.find("a", class_="product-tile__image-link")
                url = "https://shop.lululemon.com" + link_element.get("href") if link_element and link_element.get("href") else "Unknown"
                
                # Extract image URL
                img_element = tile.find("img")
                image_url = ""
                if img_element and img_element.get("srcset"):
                    # Extract the first image URL from srcset
                    srcset = img_element.get("srcset")
                    image_urls = re.findall(r'(https://[^\s]+)', srcset)
                    image_url = image_urls[0] if image_urls else ""
                
                # Create product dictionary
                product = {
                    'index': len(products) + 1,
                    'date': pd.Timestamp.today().strftime('%Y-%m-%d'),
                    'brand': "lululemon",
                    'name': name,
                    'price': price,
                    'url': url,
                    'image_url': image_url
                }
                products.append(product)
            except Exception as e:
                print(f"Error processing product tile: {e}")
        
        # Save to CSV
        if products:
            df = pd.DataFrame(products)
            csv_filename = 'lululemon_products.csv'
            df.to_csv(csv_filename, index=False)
            print(f"Successfully scraped {len(df)} products. Data saved to {csv_filename}.")
            print("\nSample data:")
            print(df.head())
        else:
            print("No product data found!")
            
    except Exception as e:
        print(f"Error in extract_product_data: {e}")
    
except Exception as e:
    print(f"An error occurred in main: {e}")

finally:
    # Close the driver
    print("Closing browser...")
    if 'driver' in locals():
        driver.quit()

creds_path = os.environ.get('CREDS_PATH', '/Users/pleng/python/pleng.io/spatial-framing-452703-g4-d9e7337e6b02.json')

# Authenticate with Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
client = gspread.authorize(creds)

# Open the Google Sheet (replace with your Sheet ID)
SHEET_ID = os.environ.get('SHEET_ID', "1G4cuYs_7qD1ft6OEhovLjj8zowQc92yYHQz2gSmLpp8")
sheet_name = "lululemon"
sheet = client.open_by_key(SHEET_ID).worksheet(sheet_name)

# Convert DataFrame to a list of lists for Google Sheets
data_to_append = df.values.tolist()

# Append new data (don't overwrite existing)
sheet.append_rows(data_to_append)

print("Data successfully uploaded to Google Sheets!")

# %%



