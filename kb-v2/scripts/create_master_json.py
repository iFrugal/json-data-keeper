import csv
import json
import os
from collections import defaultdict
from urllib.parse import urlparse

def extract_file_extension(url):
    """Extract file extension from URL"""
    if not url:
        return 'jpg'  # default fallback

    parsed = urlparse(url)
    # Get the path and extract extension
    path = parsed.path
    if '.' in path:
        return path.split('.')[-1].lower()
    return 'jpg'  # default fallback

def create_sample_products_data():
    """Create sample products data that will be used for all products.json files"""
    return {
        "total": 1,
        "products": [
            {
                "_id": "68822788f5928b1d05cb013a",
                "name": "Tata Tea Agni Special Blend Tea",
                "image": [
                    "http://res.cloudinary.com/ddwitlcay/image/upload/v1753360223/category-images/xnwiqptw7ovmzbx1hesx.jpg",
                    "http://res.cloudinary.com/ddwitlcay/image/upload/v1753360239/category-images/ryfwkotcr6d4sgw6kttl.jpg",
                    "http://res.cloudinary.com/ddwitlcay/image/upload/v1753360247/category-images/kjqttyakrhhu4pbkxkub.jpg",
                    "http://res.cloudinary.com/ddwitlcay/image/upload/v1753360254/category-images/ieoarqif207ejvdfarrh.jpg",
                    "http://res.cloudinary.com/ddwitlcay/image/upload/v1753360261/category-images/hpfhqiacoqsj1zxxwjfc.jpg"
                ],
                "category": [
                    "686551d0216f5ba9b411d744"
                ],
                "subCategory": [
                    "686aa3fb43c48c6b25c3b722"
                ],
                "unit": "1 Kg",
                "stock": 10,
                "price": 150,
                "discount": 1,
                "description": "\nTata Tea Agni offers a strong cup of tea at an affordable price, energizing people to overcome any challenges along the way. Tata Tea Agni's 10% extra strong leaves give a strong taste in every cup. With a special blend of tea leaves, it offers freshness & rich fullness that will leave you longing for more. Enjoy it whenever you long for a strong cup of tea to awaken your mind and get rejuvenated.\n",
                "more_details": {
                    "Key Features": "Enjoy a strong cup of tea with Tata Tea Agni Strong Leaf Tea. Make your mornings strong with 10% extra strong leaves. Tata Agni leaf tea has a special blend of tea leaves. Make anytime tea time with a refreshing sip of your favorite tea",
                    "Storage Tips": "Once opened, transfer the contents into an airtight container and keep the lid tightly closed after each use.",
                    "Type": "Leaf Tea",
                    "Shelf Life": "12 Months",
                    "Manufacturer Details": "Tata Consumer Products Ltd, 3rd Floor Block C, Kirloskar Business Park, Hebbal, Bengaluru 560024",
                    "Marketed By": "Tata Consumer Products Ltd, 3rd Floor Block C, Kirloskar Business Park, Hebbal, Bengaluru 560024",
                    "Return Policy": " This Item is non-returnable. For a damaged, defective, incorrect or expired item, you can request a replacement within 72 hours of delivery. In case of an incorrect item, you may raise a replacement or return request only if the item is sealed/ unopened/ unused and in original condition."
                },
                "publish": True,
                "createdAt": "2025-07-24T12:31:04.900Z",
                "updatedAt": "2025-07-24T12:31:04.900Z",
                "__v": 0
            }
        ]
    }

def create_json_structure(csv_file_path, base_dir="../master", base_image_url="https://cdn.jsdelivr.net/gh/iFrugal/json-data-keeper@main/kb-v2"):
    """
    Create JSON files from CSV data:
    - master/category/all.json (all categories)
    - master/category/{category_id}/sub-categories.json (subcategories for each category)
    - master/category/{category_id}/sub-category/{subcategory_id}/products.json (products for each subcategory)
    """

    # Data structures to store processed data
    categories = {}
    subcategories_by_category = defaultdict(dict)
    all_subcategory_paths = []  # To track all subcategory paths for products.json creation

    # Statistics
    total_rows = 0
    unique_categories = set()
    unique_subcategories = set()

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            print("Processing CSV data...")

            for row in reader:
                total_rows += 1

                # Extract and clean data
                category_order = row.get('category_order', '').strip()
                category_id = row.get('category_id', '').strip()
                category_name = row.get('category_name', '').strip()
                category_image = row.get('category_image', '').strip()

                subcategory_order = row.get('subcategory_order', '').strip()
                subcategory_id = row.get('subcategory_id', '').strip()
                subcategory_name = row.get('subcategory_name', '').strip()
                subcategory_image = row.get('subcategory_image', '').strip()

                # Process category data (avoid duplicates)
                if category_id and category_id not in categories:
                    # Extract original file extension from category image URL
                    category_ext = extract_file_extension(category_image)
                    # Create new image URL
                    new_category_image = f"{base_image_url}/images/category/{category_id}/{category_id}.{category_ext}"

                    categories[category_id] = {
                        "id": category_id,
                        "name": category_name,
                        "order": int(category_order) if category_order.isdigit() else 0,
                        "image": new_category_image
                    }
                    unique_categories.add(category_id)
                    print(f"Added category: {category_id} - {category_name}")

                # Process subcategory data
                if subcategory_id and category_id:
                    # Extract original file extension from subcategory image URL
                    subcategory_ext = extract_file_extension(subcategory_image)
                    # Create new image URL
                    new_subcategory_image = f"{base_image_url}/images/category/{category_id}/sub-category/{subcategory_id}.{subcategory_ext}"

                    subcategories_by_category[category_id][subcategory_id] = {
                        "id": subcategory_id,
                        "name": subcategory_name,
                        "order": int(subcategory_order) if subcategory_order.isdigit() else 0,
                        "image": new_subcategory_image
                    }
                    unique_subcategories.add(f"{category_id}_{subcategory_id}")

                    # Track subcategory path for products.json creation
                    subcategory_path = {
                        "category_id": category_id,
                        "subcategory_id": subcategory_id,
                        "category_name": category_name,
                        "subcategory_name": subcategory_name
                    }
                    if subcategory_path not in all_subcategory_paths:
                        all_subcategory_paths.append(subcategory_path)

                    print(f"Added subcategory: {subcategory_id} - {subcategory_name} (under {category_id})")

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file_path}' not found!")
        return
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return

    # Create directory structure
    category_dir = os.path.join(base_dir, "category")
    os.makedirs(category_dir, exist_ok=True)

    # 1. Create master/category/all.json with all categories
    all_categories_file = os.path.join(category_dir, "all.json")

    # Convert categories dict to sorted list
    categories_list = list(categories.values())
    categories_list.sort(key=lambda x: x['order'])

    categories_data = {
        "total": len(categories_list),
        "categories": categories_list
    }

    try:
        with open(all_categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories_data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Created: {all_categories_file}")
    except Exception as e:
        print(f"❌ Error creating {all_categories_file}: {str(e)}")

    # 2. Create individual subcategory files for each category
    subcategory_files_created = 0

    for category_id, subcategories in subcategories_by_category.items():
        # Create directory for this category
        category_specific_dir = os.path.join(category_dir, category_id)
        os.makedirs(category_specific_dir, exist_ok=True)

        # Create sub-categories.json file
        subcategories_file = os.path.join(category_specific_dir, "sub-categories.json")

        # Convert subcategories dict to sorted list
        subcategories_list = list(subcategories.values())
        subcategories_list.sort(key=lambda x: x['order'])

        subcategories_data = {
            "parent": {
                "id": category_id,
                "name": categories.get(category_id, {}).get('name', '')
            },
            "total": len(subcategories_list),
            "subcategories": subcategories_list
        }

        try:
            with open(subcategories_file, 'w', encoding='utf-8') as f:
                json.dump(subcategories_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Created: {subcategories_file}")
            subcategory_files_created += 1
        except Exception as e:
            print(f"❌ Error creating {subcategories_file}: {str(e)}")

    # 3. Create products.json files for each subcategory
    products_files_created = 0
    sample_products_data = create_sample_products_data()

    for subcategory_info in all_subcategory_paths:
        category_id = subcategory_info["category_id"]
        subcategory_id = subcategory_info["subcategory_id"]

        # Create sub-category directory
        subcategory_dir = os.path.join(category_dir, category_id, "sub-category", subcategory_id)
        os.makedirs(subcategory_dir, exist_ok=True)

        # Create products.json file
        products_file = os.path.join(subcategory_dir, "products.json")

        # Create products data with parent information
        products_data = {
            "parent": {
                "category_id": category_id,
                "category_name": subcategory_info["category_name"],
                "subcategory_id": subcategory_id,
                "subcategory_name": subcategory_info["subcategory_name"]
            },
            "total": sample_products_data["total"],
            "products": sample_products_data["products"]
        }

        try:
            with open(products_file, 'w', encoding='utf-8') as f:
                json.dump(products_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Created: {products_file}")
            products_files_created += 1
        except Exception as e:
            print(f"❌ Error creating {products_file}: {str(e)}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"JSON GENERATION SUMMARY")
    print(f"{'='*60}")
    print(f"CSV rows processed: {total_rows}")
    print(f"Unique categories: {len(unique_categories)}")
    print(f"Unique subcategories: {len(unique_subcategories)}")
    print(f"Category files created: 1 (all.json)")
    print(f"Subcategory files created: {subcategory_files_created}")
    print(f"Products files created: {products_files_created}")
    print(f"Total JSON files created: {1 + subcategory_files_created + products_files_created}")

    # Show directory structure
    print(f"\nDirectory structure created:")
    print(f"📁 {base_dir}/")
    print(f"  📁 category/")
    print(f"    📄 all.json")

    for category_id in sorted(subcategories_by_category.keys()):
        print(f"    📁 {category_id}/")
        print(f"      📄 sub-categories.json")

        # Show subcategory structure
        subcategories = subcategories_by_category[category_id]
        for subcategory_id in sorted(subcategories.keys()):
            print(f"      📁 sub-category/")
            print(f"        📁 {subcategory_id}/")
            print(f"          📄 products.json")

    # Show sample of generated data
    print(f"\nSample from all.json:")
    print("-" * 30)
    if categories_list:
        sample_category = categories_list[0]
        print(json.dumps(sample_category, indent=2, ensure_ascii=False))

    if subcategories_by_category:
        first_category = next(iter(subcategories_by_category))
        first_subcategories = list(subcategories_by_category[first_category].values())
        if first_subcategories:
            print(f"\nSample from {first_category}/sub-categories.json:")
            print("-" * 40)
            print(json.dumps(first_subcategories[0], indent=2, ensure_ascii=False))

    # Show sample products.json structure
    if all_subcategory_paths:
        first_subcategory = all_subcategory_paths[0]
        print(f"\nSample products.json structure:")
        print("-" * 40)
        sample_products_structure = {
            "parent": {
                "category_id": first_subcategory["category_id"],
                "category_name": first_subcategory["category_name"],
                "subcategory_id": first_subcategory["subcategory_id"],
                "subcategory_name": first_subcategory["subcategory_name"]
            },
            "total": 1,
            "products": [
                {
                    "_id": "68822788f5928b1d05cb013a",
                    "name": "Tata Tea Agni Special Blend Tea",
                    "unit": "1 Kg",
                    "price": 150,
                    "stock": 10,
                    "...": "... (full product data)"
                }
            ]
        }
        print(json.dumps(sample_products_structure, indent=2, ensure_ascii=False))

def validate_csv_structure(csv_file_path):
    """Validate that the CSV has the expected columns"""
    expected_columns = [
        'category_order', 'category_id', 'category_name', 'category_image',
        'subcategory_order', 'subcategory_id', 'subcategory_name', 'subcategory_image'
    ]

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            actual_columns = reader.fieldnames

            print(f"CSV columns found: {actual_columns}")

            missing_columns = set(expected_columns) - set(actual_columns)
            if missing_columns:
                print(f"⚠️  Missing columns: {missing_columns}")
                return False
            else:
                print("✅ All expected columns found!")
                return True

    except Exception as e:
        print(f"Error validating CSV: {str(e)}")
        return False

def main():
    """Main execution function"""
    csv_file_path = "categories_fixed.csv"  # Change this to your CSV file path
    base_dir = "../master"               # Changed as requested
    base_image_url = "https://cdn.jsdelivr.net/gh/iFrugal/json-data-keeper@main/kb-v2"  # Base URL for images

    print("CSV to JSON Structure Generator (Enhanced)")
    print("="*50)
    print(f"Base directory: {base_dir}")
    print(f"Base image URL: {base_image_url}")

    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file '{csv_file_path}' not found!")
        print("Please update the 'csv_file_path' variable with the correct path.")
        return

    # Validate CSV structure
    print("Validating CSV structure...")
    if not validate_csv_structure(csv_file_path):
        print("❌ CSV validation failed. Please check your CSV file structure.")
        return

    # Generate JSON files
    print(f"\nGenerating JSON files in '{base_dir}' directory...")
    create_json_structure(csv_file_path, base_dir, base_image_url)

    print(f"\n✅ All done! Check the '{base_dir}' directory for generated JSON files.")

if __name__ == "__main__":
    main()