# Alo Yoga Product Details Scraper

This script extracts detailed information from Alo Yoga product pages, including:
1. Product Description
2. Sizes Available
3. Fabrication/Material

## Prerequisites

Ensure you have the required dependencies installed:
```
pip install -r requirements.txt
```

## Usage

### 1. Prepare a CSV file with product URLs

Create a CSV file containing Alo Yoga product URLs. The file should have a column named 'URL' (or specify a different column name using the `--url_column` parameter).

Example CSV format:
```
URL
https://www.aloyoga.com/products/w5858r-airlift-high-waist-flutter-legging-black
https://www.aloyoga.com/products/m4031r-the-conquer-reform-short-sleeve-black
```

### 2. Run the script

Basic usage:
```
python alo_product_details_scraper.py your_input_file.csv
```

With optional parameters:
```
python alo_product_details_scraper.py your_input_file.csv --url_column="Product URL" --output_csv="detailed_results.csv"
```

### Parameters

- `input_csv`: Path to the CSV file containing product URLs (required)
- `--url_column`: Name of the column containing URLs (default: 'URL')
- `--output_csv`: Path to save the output CSV file (default: 'alo_product_details.csv')

## Output

The script will generate a CSV file containing all the original columns from your input file plus the following additional columns:

- Product Name
- Price
- URL
- Image URL
- Product Description
- Sizes Available
- Fabrication

## Troubleshooting

If you encounter issues with the script:

1. **Selenium WebDriver errors**: Make sure you have Chrome installed and that the ChromeDriver version is compatible with your Chrome version.

2. **Website structure changes**: If Alo Yoga updates their website structure, the selectors in the script may need to be updated.

3. **Rate limiting**: If you're processing many URLs, the website might rate-limit your requests. Try adding longer delays between requests by modifying the `time.sleep()` values in the script.

4. **Missing data**: Some products might not have all the information available. The script will output "Not found" for fields it couldn't extract.