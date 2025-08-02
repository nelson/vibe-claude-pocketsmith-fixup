import os
import sys
import json
from pocketsmith import PocketsmithClient


def main():
    # Get API key from environment variable
    api_key = os.getenv('POCKETSMITH_API_KEY')
    
    if not api_key:
        print("Error: POCKETSMITH_API_KEY environment variable not set")
        print("Please set it with: export POCKETSMITH_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    try:
        # Initialize PocketSmith client
        client = PocketsmithClient(api_key)
        
        # Get user info first to get user ID
        user_info = client.users.get_me()
        user_id = user_info['id']
        
        # Fetch categories
        print("Fetching categories from PocketSmith...")
        categories = client.categories.list_categories(user_id)
        
        if not categories:
            print("No categories found in your PocketSmith account.")
            return
        
        # Convert categories to serializable format and save to JSON file
        categories_data = []
        for category in categories:
            cat_dict = {
                'id': category.get('id'),
                'title': category.get('title'),
                'colour': category.get('colour'),
                'parent_id': category.get('parent_id'),
                'is_bill': category.get('is_bill'),
                'is_transfer': category.get('is_transfer'),
                'created_at': category.get('created_at').isoformat() if category.get('created_at') else None,
                'updated_at': category.get('updated_at').isoformat() if category.get('updated_at') else None
            }
            categories_data.append(cat_dict)
        
        with open('categories.json', 'w') as f:
            json.dump(categories_data, f, indent=2)
        print(f"Saved {len(categories)} categories to categories.json")
        
        print(f"\nFound {len(categories)} categories:")
        print("-" * 50)
        
        for category in categories:
            print(f"ID: {category.get('id', 'N/A')}")
            print(f"Title: {category.get('title', 'N/A')}")
            if category.get('colour'):
                print(f"Color: {category['colour']}")
            if category.get('parent_id'):
                print(f"Parent ID: {category['parent_id']}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error accessing PocketSmith API: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
