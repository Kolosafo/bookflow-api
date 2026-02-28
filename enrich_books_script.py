import os
import django
import json
import time

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookflow_api.settings")
django.setup()

from books.utils import search_books

INPUT_FILE = "static/categories/general.json"
OUTPUT_FILE = "static/categories/general_detailed.json"
TARGET_CATEGORY = "Productivity, Discipline & Habits"

def enrich_books():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        return

    # Load input data
    with open(INPUT_FILE, 'r') as f:
        input_data = json.load(f)

    # Load existing output data if it exists to preserve work
    output_data = {"categories": []}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            try:
                output_data = json.load(f)
                print(f"Loaded existing data from {OUTPUT_FILE}")
            except json.JSONDecodeError:
                print(f"Warning: {OUTPUT_FILE} exists but is empty or invalid. Starting fresh.")
    
    total_books = 0
    
    # helper to find or create category object in output_data
    def get_output_category(cat_name):
        for cat in output_data["categories"]:
            if cat["category"] == cat_name:
                return cat
        # Not found, create new structure
        new_cat = {"category": cat_name, "books": {}}
        output_data["categories"].append(new_cat)
        return new_cat

    # Iterate over input categories
    for category_data in input_data.get("categories", []):
        category_name = category_data.get("category")
        
        # Check if we should process this category
        if category_name != TARGET_CATEGORY:
            print(f"Skipping category: '{category_name}'")
            # Ensure it exists in output (as simple list or preserve what we have)
            # For now, let's just ensure the structure exists if we want to be thorough,
            # but user only asked for this specific one. 
            # To avoid overwriting other categories if we run this script correctly in future:
            # We just skip logic. If it's a new run, other categories won't be in output_data unless we copy them.
            # Let's copy them as-is (list of strings) if they don't exist in output yet.
            
            out_cat = get_output_category(category_name)
            if not out_cat.get("books"): # if empty or missing, populate with original list
                 out_cat["books"] = category_data.get("books", [])
            continue
        
        print(f"Processing category: '{category_name}'")
        items = category_data.get("books", [])
        
        # Get output category object
        out_cat = get_output_category(category_name)
        
        # If "books" is already a dict (processed), let's use it as base
        # If it's a list (unprocessed), start fresh dict
        current_books_dict = {}
        if isinstance(out_cat.get("books"), dict):
            current_books_dict = out_cat["books"]
        
        # items is a list of strings
        for book_query in items:
            # Skip if already processed
            if book_query in current_books_dict and current_books_dict[book_query].get("kind"):
                 print(f"  Skipping '{book_query}' (already valid).")
                 continue

            print(f"  Searching for: '{book_query}'")
            try:
                result = search_books(book_query, max_results=1)
                
                book_details = {}
                if result and 'items' in result and len(result['items']) > 0:
                    book_details = result['items'][0]
                    print("    -> Found book.")
                else:
                    print("    -> Book not found.")
                
                current_books_dict[book_query] = book_details
                total_books += 1
                
                time.sleep(0.5)
            except Exception as e:
                print(f"    -> Error searching for '{book_query}': {e}")
                current_books_dict[book_query] = {}
        
        out_cat["books"] = current_books_dict
        
    # Write the enriched data to a new file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nDone! Processed {total_books} new books.")
    print(f"Saved enriched data to {OUTPUT_FILE}")

if __name__ == "__main__":
    enrich_books()
