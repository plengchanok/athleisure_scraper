import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse
import os
import re
import random
import json
from urllib.parse import urlparse, parse_qs

def get_user_agent():
    """Return a random user agent string"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def get_product_handle(url):
    """Extract the product handle from the URL"""
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) >= 2 and path_parts[0] == 'products':
        return path_parts[1]
    return None

def extract_product_details(url):
    """Extract product details from a given URL using requests and BeautifulSoup"""
    print(f"Processing URL: {url}")
    
    try:
        # Extract product handle from URL
        product_handle = get_product_handle(url)
        if not product_handle:
            raise ValueError(f"Could not extract product handle from URL: {url}")
        
        # Try to get product data from Shopify API
        api_url = f"https://www.aloyoga.com/products/{product_handle}.js"
        
        # Set up headers to mimic a browser
        headers = {
            "User-Agent": get_user_agent(),
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.aloyoga.com/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "max-age=0"
        }
        
        # Make the request to the Shopify API
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse the JSON response
        product_data = json.loads(response.text)
        
        # Extract product information from the JSON data
        product_name = product_data.get('title', 'Not found')
        product_price = f"${float(product_data.get('price', 0)) / 100:.2f}"
        product_description = product_data.get('description', 'Not found')
        
        # Extract available sizes
        sizes_available = []
        for variant in product_data.get('variants', []):
            if 'option1' in variant and variant['option1'] and variant['option1'] not in sizes_available:
                sizes_available.append(variant['option1'])
        sizes_str = ", ".join(sizes_available) if sizes_available else "Not found"
        
        # Extract image URL
        image_url = "Not found"
        if product_data.get('featured_image'):
            image_url = product_data['featured_image']
        elif product_data.get('images') and len(product_data['images']) > 0:
            image_url = product_data['images'][0]
        
        # Extract fabrication/material from description
        fabrication = "Not found"
        if product_description != "Not found":
            # Common patterns for fabric information
            fabric_patterns = [
                r"(?:Fabric|Material|Fabrication):\s*([^\.]+)",
                r"(?:Made of|Made from|Crafted from|Crafted with|Constructed from|Constructed with)\s+([^\.]+)",
                r"(\d+%\s*[A-Za-z]+(?:\s*,\s*\d+%\s*[A-Za-z]+)*)"
            ]
            
            for pattern in fabric_patterns:
                fabric_match = re.search(pattern, product_description, re.IGNORECASE)
                if fabric_match:
                    fabrication = fabric_match.group(1).strip()
                    break
        
        # If we couldn't get the data from the API, try the regular HTML approach
        if product_name == "Not found" or product_price == "$0.00":
            print("API data incomplete, trying HTML approach...")
            
            # Set up headers for HTML request
            html_headers = {
                "User-Agent": get_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            }
            
            try:
                # Make the request to the product page
                html_response = requests.get(url, headers=html_headers, timeout=30)
                html_response.raise_for_status()
                
                # Parse the HTML
                soup = BeautifulSoup(html_response.text, 'html.parser')
                
                # Extract product name
                name_elem = soup.select_one('h1.product-name')
                if name_elem:
                    product_name = name_elem.text.strip()
                
                # Extract product price
                price_elem = soup.select_one('.product-price')
                if price_elem:
                    product_price = price_elem.text.strip()
                
                # Extract product description
                desc_elem = soup.select_one('.product-description')
                if desc_elem:
                    product_description = desc_elem.text.strip()
                
                # Extract available sizes
                sizes_available = []
                size_elements = soup.select('.size-selector .size-option')
                for size_elem in size_elements:
                    size_text = size_elem.text.strip()
                    if size_text:
                        sizes_available.append(size_text)
                
                # If no sizes found, try alternative selectors
                if not sizes_available:
                    size_elements = soup.select('.swatch-element')
                    for size_elem in size_elements:
                        size_text = size_elem.text.strip()
                        if size_text:
                            sizes_available.append(size_text)
                
                # If still no sizes found, try more selectors
                if not sizes_available:
                    size_elements = soup.select('[data-option-name="Size"] .swatch-element')
                    for size_elem in size_elements:
                        size_text = size_elem.text.strip()
                        if size_text:
                            sizes_available.append(size_text)
                
                if sizes_available:
                    sizes_str = ", ".join(sizes_available)
                
                # Try to find fabrication in dedicated sections
                fabric_section = soup.select_one('.fabric-content, .material-content, .product-fabric')
                if fabric_section:
                    fabrication = fabric_section.text.strip()
                
                # Get image URL
                img_elem = soup.select_one('.product-image img')
                if img_elem and 'src' in img_elem.attrs:
                    image_url = img_elem['src']
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url
                    elif not image_url.startswith("http"):
                        image_url = "https://www.aloyoga.com" + image_url
            
            except Exception as html_error:
                print(f"HTML approach failed: {html_error}")
                # Continue with the API data we already have
        
        return {
            'Product Name': product_name,
            'Price': product_price,
            'URL': url,
            'Image URL': image_url,
            'Product Description': product_description,
            'Sizes Available': sizes_str,
            'Fabrication': fabrication
        }
    
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return {
            'Product Name': "Error",
            'Price': "Error",
            'URL': url,
            'Image URL': "Error",
            'Product Description': "Error",
            'Sizes Available': "Error",
            'Fabrication': "Error"
        }

def main():
    parser = argparse.ArgumentParser(description='Scrape Alo Yoga product details from URLs in a CSV file')
    parser.add_argument('input_csv', help='Path to CSV file containing product URLs')
    parser.add_argument('--url_column', default='URL', help='Column name containing URLs in the CSV')
    parser.add_argument('--output_csv', default='alo_product_details.csv', help='Output CSV file path')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests in seconds')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_csv):
        print(f"Error: Input file {args.input_csv} not found")
        return
    
    # Read the CSV file
    try:
        df = pd.read_csv(args.input_csv)
        if args.url_column not in df.columns:
            print(f"Error: Column '{args.url_column}' not found in the CSV file")
            print(f"Available columns: {', '.join(df.columns)}")
            return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    try:
        # Initialize list to store results
        results = []
        
        # Process each URL
        total_urls = len(df)
        for index, row in df.iterrows():
            url = row[args.url_column]
            if pd.isna(url) or not url.startswith('http'):
                print(f"Skipping invalid URL at row {index+1}: {url}")
                continue
            
            print(f"Processing URL {index+1}/{total_urls}: {url}")
            
            # Extract product details
            product_data = extract_product_details(url)
            
            # Add any existing columns from the input CSV
            for col in df.columns:
                if col != args.url_column and col not in product_data:
                    product_data[col] = row[col]
            
            results.append(product_data)
            
            # Add a small delay between requests to avoid overloading the server
            if index < total_urls - 1:  # Don't delay after the last URL
                delay = args.delay + random.uniform(0, 1)  # Add some randomness to the delay
                print(f"Waiting {delay:.2f} seconds before next request...")
                time.sleep(delay)
        
        # Create DataFrame from results
        results_df = pd.DataFrame(results)
        
        # Save to CSV
        results_df.to_csv(args.output_csv, index=False)
        print(f"Data successfully saved to {args.output_csv}")
    
    except Exception as e:
        print(f"Error in script: {e}")
        
        # If we have partial results, try to save them
        if results:
            try:
                partial_df = pd.DataFrame(results)
                partial_output = f"partial_{args.output_csv}"
                partial_df.to_csv(partial_output, index=False)
                print(f"Partial data saved to {partial_output}")
            except Exception as save_error:
                print(f"Error saving partial results: {save_error}")

if __name__ == "__main__":
    main()