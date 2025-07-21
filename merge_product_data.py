import pandas as pd
import argparse
import os

def merge_product_data(original_data_path, new_details_path, output_path):
    """
    Merge original product data with newly collected product details.
    
    Args:
        original_data_path (str): Path to the original product data CSV
        new_details_path (str): Path to the CSV with new product details
        output_path (str): Path to save the merged data
    """
    # Load the original data
    original_df = pd.read_csv(original_data_path)
    
    # Load the new details
    new_details_df = pd.read_csv(new_details_path)
    
    # Ensure both DataFrames have a URL column for merging
    if 'URL' not in original_df.columns:
        print("Error: Original data must have a 'URL' column")
        return False
    
    if 'URL' not in new_details_df.columns:
        print("Error: New details must have a 'URL' column")
        return False
    
    # Merge the DataFrames on the URL column
    merged_df = pd.merge(original_df, new_details_df, on='URL', how='left', suffixes=('', '_new'))
    
    # For columns that exist in both DataFrames, prefer the new values if they exist
    for col in new_details_df.columns:
        if col != 'URL' and col in original_df.columns:
            # Create a new column name to avoid conflicts
            new_col = f"{col}_new"
            if new_col in merged_df.columns:
                # Replace values in the original column with non-empty values from the new column
                merged_df[col] = merged_df.apply(
                    lambda row: row[new_col] if pd.notna(row[new_col]) and row[new_col] != "" else row[col],
                    axis=1
                )
                # Drop the temporary column
                merged_df = merged_df.drop(columns=[new_col])
    
    # Add new columns that don't exist in the original DataFrame
    for col in new_details_df.columns:
        if col != 'URL' and col not in original_df.columns:
            merged_df[col] = new_details_df[col]
    
    # Save the merged DataFrame
    merged_df.to_csv(output_path, index=False)
    print(f"Merged data saved to {output_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Merge original product data with new product details')
    parser.add_argument('original_data', help='Path to the original product data CSV')
    parser.add_argument('new_details', help='Path to the CSV with new product details')
    parser.add_argument('--output', default='merged_product_data.csv', help='Path to save the merged data')
    
    args = parser.parse_args()
    
    # Check if input files exist
    if not os.path.exists(args.original_data):
        print(f"Error: Original data file {args.original_data} not found")
        return
    
    if not os.path.exists(args.new_details):
        print(f"Error: New details file {args.new_details} not found")
        return
    
    # Merge the data
    merge_product_data(args.original_data, args.new_details, args.output)

if __name__ == "__main__":
    main()