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

# Setup Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920x1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--lang=en")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the Alo Yoga product page
url = "https://www.aloyoga.com/collections/bestsellers"
driver.get(url)

# Wait for page to load
time.sleep(5)

# Step 1: Remove the iframe
try:
    iframe = driver.find_element(By.ID, "attentive_creative")  # Find the iframe
    driver.execute_script("arguments[0].remove();", iframe)  # Remove iframe using JavaScript
    print("Iframe removed successfully.")
    time.sleep(2)  # Wait for iframe to disappear
except Exception as e:
    print("No blocking iframe detected:", e)

# Step 2: Now, close the pop-up
try:
    pop_up = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "osano-cm-dialog"))
    )
    close_button = pop_up.find_element(By.CLASS_NAME, "osano-cm-dialog__close")
    close_button.click()
    print("Pop-up closed successfully.")
    time.sleep(2)

except Exception as e:
    print("No pop-up detected or issue closing it:", e)

# Fix scrolling issue
driver.execute_script("document.documentElement.style.overflow = 'auto';")

# Scroll down
for _ in range(3):
    driver.execute_script("window.scrollBy(0, window.innerHeight);")
    time.sleep(2)

html = driver.find_element(By.TAG_NAME, 'html')

for _ in range(3):
    html.send_keys(Keys.PAGE_DOWN)
    time.sleep(2)

def scroll_and_wait(driver, num_scrolls=5, wait_time=2):
    actions = ActionChains(driver)
    for _ in range(num_scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(wait_time)
        actions.move_to_element(driver.find_element(By.TAG_NAME, 'body')).perform()

scroll_and_wait(driver)

# with open("debug_page.html", "w", encoding="utf-8") as f:
#     f.write(driver.page_source)

# print("Saved HTML to debug_page.html. Open it in a browser to inspect.")

# Get the page source after interactions
page_source = driver.page_source

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
    
    # Extract product image - using the correct selectors from the HTML
    img_elem = item.select_one('img.normal') or item.select_one('img')
    if img_elem and 'src' in img_elem.attrs:
        img_url = img_elem['src']
        if not img_url.startswith('http'):
            img_url = 'https:' + img_url if img_url.startswith('//') else 'https://www.aloyoga.com' + img_url
        product_images.append(img_url)
    else:
        product_images.append("Image not found")

# Create a DataFrame with the extracted information
df = pd.DataFrame({
    'Index': range(1, len(product_names) + 1),
    'Date': [pd.Timestamp.today().strftime('%Y-%m-%d')] * len(product_names),
    'Product Name': product_names,
    'Price': product_prices,
    'URL': product_urls,
    'Image URL': product_images
})

# Close browser
driver.quit()

df.head()

creds_path = os.environ.get('CREDS_PATH', '/Users/pleng/python/pleng.io/spatial-framing-452703-g4-d9e7337e6b02.json')

# Authenticate with Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
client = gspread.authorize(creds)

# Open the Google Sheet (replace with your Sheet ID)
SHEET_ID = os.environ.get('SHEET_ID', "1G4cuYs_7qD1ft6OEhovLjj8zowQc92yYHQz2gSmLpp8")
sheet = client.open_by_key(SHEET_ID).sheet1
# Convert DataFrame to a list of lists for Google Sheets
data_to_append = df.values.tolist()

# Append new data (don't overwrite existing)
sheet.append_rows(data_to_append)

print("Data successfully uploaded to Google Sheets!")

# %%



