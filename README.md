# Athleisure Brand Scraper

## Overview
This repository contains scrapers for various athleisure brands to extract product information from their websites. It automates the data collection process, allowing for structured extraction, transformation, and storage in Google Sheets.

## Dashboard
To view the Looker dashboard please click [here] (https://lookerstudio.google.com/u/0/reporting/22020cb3-3537-4db3-a347-1a01886eaa15/page/p_l6vob0yisd)

## Features
- Scrapes product data from multiple athleisure brands:
  - Alo Yoga (bestsellers and new arrivals)
  - Lululemon (bestsellers and new arrivals)
  - Vuori (women's new arrivals)
  - Beyond Yoga (new arrivals)
  - Athleta (new arrivals)
- Extracts relevant details (product names, prices, URLs, and image URLs)
- Cleans and structures the extracted data for easy analysis
- Saves output directly to Google Sheets for easy access and visualization

## Requirements
To run these scrapers, ensure you have the following dependencies installed:

- Python 3.x
- Selenium
- WebDriver Manager
- BeautifulSoup4
- Pandas
- gspread (for Google Sheets integration)
- Google Auth libraries

You can install all dependencies using:
```sh
pip install -r requirements.txt
```

## Usage
You can run individual scrapers or run all of them at once:

1. To run all scrapers:
   ```sh
   python run_all_scrapers.py
   ```

2. To run individual scrapers:
   ```sh
   python scraper_alo_new.py
   python scraper_lululemon_new.py
   python scraper_vuori.py
   python scraper_beyond_yoga.py
   python scraper_athleta.py
   ```

3. Set up Google Sheets credentials:
   - Create a service account in Google Cloud Console
   - Download the JSON credentials file
   - Set the `CREDS_PATH` environment variable to point to your credentials file
   - Set the `SHEET_ID` environment variable to your Google Sheet ID

## Output
- The extracted data is saved directly to Google Sheets in separate worksheets for each brand.

## Customization
- Update the URLs in each scraper to target different pages or categories
- Modify the parsing logic to extract additional fields
- Adjust the scrolling parameters to ensure all products are loaded
- Change the Google Sheets worksheet names or structure

## Notes
- Ensure compliance with each brand's terms of service before scraping
- The scrapers include rate limiting and delays to prevent being blocked
- Each scraper handles common popup and modal dialogs that might interfere with scraping

## Data Structure
Each scraper collects the following information:
- Index: Sequential number for each product
- Date: Date when the data was scraped
- Brand: Name of the brand
- Product Name: Name of the product
- Price: Price of the product
- URL: Link to the product page
- Image URL: Link to the product image

## Author
Pleng Witayaweerasak

## License
This project is open-source. Modify and distribute as needed.
