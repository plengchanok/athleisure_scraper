# Manual Extraction Guide for Alo Yoga Product Details

Since automated scraping of the Alo Yoga website may be challenging due to anti-scraping measures, this guide provides instructions for manually extracting the required information.

## Information to Extract

For each product, collect the following information:

1. **Product Description**: The full text description of the product
2. **Sizes Available**: All available sizes for the product
3. **Fabrication**: The material composition of the product

## Manual Extraction Process

1. Open each product URL in a web browser
2. For each product:

   ### Product Description
   - Look for a detailed description section, usually below the product images
   - Copy the full text description

   ### Sizes Available
   - Look for the size selector, usually showing options like XS, S, M, L, XL
   - Note all available sizes (not grayed out)

   ### Fabrication
   - Look for fabric/material information in the product description
   - It may be listed as "Fabric:", "Material:", or within the description text
   - Common patterns include percentages (e.g., "87% Nylon, 13% Spandex")

3. Record this information in a spreadsheet with the following columns:
   - Product Name
   - URL
   - Product Description
   - Sizes Available
   - Fabrication

## Example

For a product like "Airlift High-Waist Flutter Legging":

- **Product Description**: "The Airlift High-Waist Flutter Legging features our signature, sculpting Airlift fabric in a high-waist, ankle-length silhouette with a feminine flutter hem. Wear it to the studio or out and about."

- **Sizes Available**: XS, S, M, L

- **Fabrication**: 87% Nylon, 13% Spandex

## Automated Approach

If you still want to try the automated approach, you can use the `alo_product_details_scraper.py` script with a CSV file containing product URLs:

```
python alo_product_details_scraper.py your_input_file.csv
```

However, please note that this may not work reliably due to website restrictions.