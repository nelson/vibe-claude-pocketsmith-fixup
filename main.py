import os
import sys
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
