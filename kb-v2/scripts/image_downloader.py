import csv
import os
import requests
from urllib.parse import urlparse
import time
from pathlib import Path

def extract_file_extension(url):
    """Extract file extension from URL"""
    parsed = urlparse(url)
    # Get the path and extract extension
    path = parsed.path
    if '.' in path:
        return path.split('.')[-1].lower()
    return 'jpg'  # default fallback

def download_image(url, filepath):
    """Download image from URL and save to filepath"""
    try:
        print(f"Downloading: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Saved: {filepath}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def process_csv_and_download_images(csv_file_path, base_images_dir="images"):
    """Main function to process CSV and download images"""

    # Track processed items to avoid duplicates
    processed_categories = set()
    processed_subcategories = set()

    # Statistics
    total_downloads = 0
    successful_downloads = 0

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                category_id = row['category_id'].strip()
                category_image = row['category_image'].strip()
                subcategory_id = row['subcategory_id'].strip()
                subcategory_image = row['subcategory_image'].strip()

                # Process category image (avoid duplicates)
                if category_id and category_image and category_id not in processed_categories:
                    category_ext = extract_file_extension(category_image)
                    category_filepath = os.path.join(
                        base_images_dir,
                        "category",
                        category_id,
                        f"{category_id}.{category_ext}"
                    )

                    print(f"\n--- Processing Category: {category_id} ---")
                    total_downloads += 1
                    if download_image(category_image, category_filepath):
                        successful_downloads += 1

                    processed_categories.add(category_id)
                    time.sleep(0.5)  # Be respectful to the server

                # Process subcategory image (avoid duplicates)
                subcategory_key = f"{category_id}_{subcategory_id}"
                if (subcategory_id and subcategory_image and
                        subcategory_key not in processed_subcategories):

                    subcategory_ext = extract_file_extension(subcategory_image)
                    subcategory_filepath = os.path.join(
                        base_images_dir,
                        "category",
                        category_id,
                        "sub-category",
                        f"{subcategory_id}.{subcategory_ext}"
                    )

                    print(f"\n--- Processing Subcategory: {subcategory_id} ---")
                    total_downloads += 1
                    if download_image(subcategory_image, subcategory_filepath):
                        successful_downloads += 1

                    processed_subcategories.add(subcategory_key)
                    time.sleep(0.5)  # Be respectful to the server

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file_path}' not found!")
        return
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        return

    # Print summary
    print(f"\n{'='*50}")
    print(f"DOWNLOAD SUMMARY")
    print(f"{'='*50}")
    print(f"Total downloads attempted: {total_downloads}")
    print(f"Successful downloads: {successful_downloads}")
    print(f"Failed downloads: {total_downloads - successful_downloads}")
    print(f"Unique categories processed: {len(processed_categories)}")
    print(f"Unique subcategories processed: {len(processed_subcategories)}")

    # Show directory structure created
    if os.path.exists(base_images_dir):
        print(f"\nDirectory structure created in: {os.path.abspath(base_images_dir)}/")
        for root, dirs, files in os.walk(base_images_dir):
            level = root.replace(base_images_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")

def main():
    """Main execution function"""
    csv_file_path = "categories_fixed.csv"  # Change this to your CSV file path

    print("Starting CSV Image Downloader...")
    print(f"Looking for CSV file: {csv_file_path}")

    if not os.path.exists(csv_file_path):
        print(f"CSV file '{csv_file_path}' not found!")
        print("Please update the 'csv_file_path' variable with the correct path to your CSV file.")
        return

    # Create base images directory
    base_dir = "../images"
    os.makedirs(base_dir, exist_ok=True)

    process_csv_and_download_images(csv_file_path, base_dir)

if __name__ == "__main__":
    main()