# Alo Yoga Product Details Tools

This collection of tools helps you extract and manage detailed product information from Alo Yoga, including product descriptions, available sizes, and fabrication details.

## Tools Included

1. **Automated Scraper** (`alo_product_details_scraper.py`): Attempts to automatically extract product details from URLs
2. **Manual Extraction Guide** (`README_MANUAL_EXTRACTION.md`): Instructions for manually collecting product details
3. **Template CSV** (`alo_product_details_template.csv`): Template for recording manually collected data
4. **Data Merger** (`merge_product_data.py`): Tool to merge original product data with newly collected details

## Workflow Options

### Option 1: Automated Extraction (May be limited by website restrictions)

1. Prepare a CSV file with product URLs (must have a column named 'URL')
2. Run the automated scraper:
   ```
   python alo_product_details_scraper.py your_input_file.csv
   ```
3. Check the output file (`alo_product_details.csv` by default) for results

### Option 2: Manual Extraction (More reliable)

1. Use the template CSV (`alo_product_details_template.csv`) or create your own
2. Follow the instructions in `README_MANUAL_EXTRACTION.md` to collect product details
3. Fill in the template CSV with the collected information
4. If you want to merge this with existing product data, use the data merger:
   ```
   python merge_product_data.py original_data.csv your_filled_template.csv --output merged_data.csv
   ```

## Detailed Tool Usage

### Automated Scraper

```
python alo_product_details_scraper.py input_csv [--url_column URL_COLUMN] [--output_csv OUTPUT_CSV] [--delay DELAY]
```

Parameters:
- `input_csv`: Path to CSV file containing product URLs (required)
- `--url_column`: Name of the column containing URLs (default: 'URL')
- `--output_csv`: Path to save the output CSV file (default: 'alo_product_details.csv')
- `--delay`: Delay between requests in seconds (default: 2.0)

### Data Merger

```
python merge_product_data.py original_data new_details [--output OUTPUT]
```

Parameters:
- `original_data`: Path to the original product data CSV (required)
- `new_details`: Path to the CSV with new product details (required)
- `--output`: Path to save the merged data (default: 'merged_product_data.csv')

## Notes on Web Scraping

Web scraping may be restricted by:
1. Anti-scraping measures on the website
2. Changes to website structure
3. Terms of service restrictions

Always check the website's terms of service before scraping, and consider using manual extraction if automated methods are not reliable or allowed.