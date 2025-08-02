#!/usr/bin/env python3
"""
PocketSmith Category Recategorisation Script

This script consolidates 63 existing categories down to 12 new categories,
using labels to retain granular information.

Usage:
    export POCKETSMITH_API_KEY='your_api_key_here'
    python recategorise.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pocketsmith import PocketsmithClient


# Category mapping from RECATEGORISE.md
CATEGORY_MAPPING = {
    7312266: {"new_category": "Bills", "label": None},  # Bills -> Bills
    7312544: {"new_category": "Dining", "label": "restaurants"},  # Eating out -> Dining
    7312549: {"new_category": "Education", "label": "classes"},  # Education -> Education
    7312554: {"new_category": "Giving", "label": "church"},  # Giving -> Giving
    7280188: {"new_category": "Groceries", "label": None},  # Groceries -> Groceries
    7312560: {"new_category": "Household", "label": None},  # Household -> Household
    7312568: {"new_category": "Income", "label": "salary"},  # Income -> Income
    7280166: {"new_category": "Bills", "label": "insurance"},  # Insurance -> Bills
    7312572: {"new_category": "Bills", "label": "medical"},  # Medical -> Bills
    7312577: {"new_category": "Mortgage", "label": "loans"},  # Mortgage -> Mortgage
    7280197: {"new_category": "Bills", "label": "subscriptions"},  # Online Services -> Bills
    7312580: {"new_category": "Shopping", "label": "hobbies"},  # Recreation -> Shopping
    7280165: {"new_category": "Bills", "label": None},  # Service Charges/Fees -> Bills
    7312587: {"new_category": "Transfer", "label": None},  # Transfer -> Transfer
    7312590: {"new_category": "Transport", "label": None},  # Transport -> Transport
    7794538: {"new_category": "Household", "label": "personal-care"},  # Clothing/Shoes -> Household
    7858322: {"new_category": "Transfer", "label": "refund"},  # Refunds/Adjustments -> Transfer
    7871181: {"new_category": "Bills", "label": "medical"},  # Healthcare/Medical -> Bills
    7896863: {"new_category": "Household", "label": "maintenance"},  # Home Maintenance -> Household
    7949656: {"new_category": "Transfer", "label": None},  # Transfers -> Transfer
    10447596: {"new_category": "Shopping", "label": None},  # Shopping -> Shopping
    10447599: {"new_category": "Bills", "label": None},  # Provider Fee -> Bills
    11049847: {"new_category": "Bills", "label": None},  # Bank Fees -> Bills
    11049943: {"new_category": "Transport", "label": "petrol"},  # Fuel -> Transport
    11049949: {"new_category": "Dining", "label": "restaurants"},  # Alcohol & Bars -> Dining
    11110102: {"new_category": "Bills", "label": None},  # Professional Services -> Bills
    11125216: {"new_category": "Bills", "label": None},  # Government Services -> Bills
    11176996: {"new_category": "Transport", "label": "car"},  # Automotive -> Transport
    11193520: {"new_category": "Household", "label": "production"},  # Computing -> Household
    11262367: {"new_category": "Mortgage", "label": "rent"},  # Housing -> Mortgage
    11421853: {"new_category": "Household", "label": "cash"},  # Cash Withdrawal -> Household
    11721802: {"new_category": "Household", "label": "production"},  # Postage -> Household
    12122497: {"new_category": "Shopping", "label": "fashion"},  # Jewellery -> Shopping
    13340188: {"new_category": "Education", "label": "childcare"},  # Child Care -> Education
    17005819: {"new_category": "Bills", "label": None},  # Business Miscellaneous -> Bills
    17291206: {"new_category": "Household", "label": "production"},  # Printing -> Household
    17298658: {"new_category": "Dining", "label": "restaurants"},  # Restaurants/Dining -> Dining
    17298661: {"new_category": "Holidays", "label": "flights"},  # Travel -> Holidays
    17310994: {"new_category": "Household", "label": "production"},  # Electronics -> Household
    17316631: {"new_category": "Bills", "label": "medical"},  # Healthcare / Medical -> Bills
    17323252: {"new_category": "Transport", "label": "petrol"},  # Gasoline/Fuel -> Transport
    17328958: {"new_category": "Mortgage", "label": "rent"},  # Rentals -> Mortgage
    17343292: {"new_category": "Bills", "label": "internet"},  # Phone -> Bills
    17417035: {"new_category": "Giving", "label": "charity"},  # Charitable Giving -> Giving
    17492305: {"new_category": "Household", "label": "production"},  # Office Supplies -> Household
    17518609: {"new_category": "Bills", "label": "utilities"},  # Utilities -> Bills
    17555794: {"new_category": "Shopping", "label": "personal-care"},  # Personal Care -> Shopping
    17571725: {"new_category": "Transport", "label": "car"},  # Automotive Expenses -> Transport
    17594012: {"new_category": "Household", "label": "personal-care"},  # Clothing -> Household
    17687411: {"new_category": "Mortgage", "label": "rent"},  # Rent -> Mortgage
    17883938: {"new_category": "Education", "label": "childcare"},  # Child/Dependent Expenses -> Education
    17887484: {"new_category": "Income", "label": "tax"},  # Taxes -> Income
    19584417: {"new_category": "Household", "label": "maintenance"},  # Home Improvement -> Household
    19584420: {"new_category": "Bills", "label": "internet"},  # Telephone Services -> Bills
    19584423: {"new_category": "Bills", "label": "subscriptions"},  # Dues and Subscriptions -> Bills
    19584426: {"new_category": "Household", "label": "pets"},  # Pets/Pet Care -> Household
    19584429: {"new_category": "Bills", "label": "internet"},  # Cable/Satellite Services -> Bills
    19584432: {"new_category": "Income", "label": "investment"},  # Securities Trades -> Income
    19584435: {"new_category": "Income", "label": "superannuation"},  # Retirement Contributions -> Income
    19965585: {"new_category": "Shopping", "label": "hobbies"},  # Hobbies -> Shopping
    20895553: {"new_category": "Household", "label": "production"},  # Postage and Shipping -> Household
    24261500: {"new_category": "Bills", "label": "utilities"},  # Power -> Bills
    24899097: {"new_category": "Mortgage", "label": "loans"},  # Loan Repayment -> Mortgage
}

PROGRESS_FILE = "recategorise_progress.json"


def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        "processed_categories": [],
        "processed_transactions": [],
        "created_categories": {},
        "start_time": None,
        "current_category": None
    }


def save_progress(progress):
    """Save progress to file"""
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def get_or_create_category(client, user_id, category_name, progress):
    """Get existing category ID or create new one"""
    # Check if we already created this category
    if category_name in progress["created_categories"]:
        return progress["created_categories"][category_name]
    
    # Check if category already exists
    categories = client.categories.list_categories(user_id)
    for cat in categories:
        if cat.title == category_name:
            progress["created_categories"][category_name] = cat.id
            save_progress(progress)
            return cat.id
    
    # Create new category
    print(f"Creating new category: {category_name}")
    new_category = client.categories.create_category(user_id, title=category_name)
    category_id = new_category.id
    progress["created_categories"][category_name] = category_id
    save_progress(progress)
    return category_id


def process_category(client, user_id, old_category_id, mapping, progress):
    """Process all transactions in a category"""
    new_category_name = mapping["new_category"]
    label = mapping["label"]
    
    print(f"\n=== Processing category {old_category_id} -> {new_category_name} ===")
    
    # Get or create new category
    new_category_id = get_or_create_category(client, user_id, new_category_name, progress)
    
    # Load all transactions
    print("Loading all transactions...")
    all_transactions = client.transactions.list_transactions(user_id)
    
    # Filter transactions for this category
    category_transactions = [
        tx for tx in all_transactions 
        if tx.category and tx.category.id == old_category_id
    ]
    
    print(f"Found {len(category_transactions)} transactions in category {old_category_id}")
    
    # Process each transaction
    processed_count = 0
    for tx in category_transactions:
        if tx.id in progress["processed_transactions"]:
            print(f"  Skipping already processed transaction {tx.id}")
            continue
        
        try:
            # Prepare update data
            update_data = {"category_id": new_category_id}
            
            # Add label if specified
            if label:
                current_labels = list(tx.labels) if tx.labels else []
                if label not in current_labels:
                    current_labels.append(label)
                update_data["labels"] = current_labels
            
            # Update transaction
            print(f"  Updating transaction {tx.id}: {tx.payee[:50]}...")
            client.transactions.update_transaction(tx.id, **update_data)
            
            # Mark as processed
            progress["processed_transactions"].append(tx.id)
            processed_count += 1
            
            # Save progress every 10 transactions
            if processed_count % 10 == 0:
                save_progress(progress)
                print(f"    Progress saved: {processed_count}/{len(category_transactions)}")
            
            # Rate limiting - small delay between API calls
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  ERROR updating transaction {tx.id}: {e}")
            # Continue processing other transactions
            continue
    
    # Final progress save
    save_progress(progress)
    print(f"Processed {processed_count} transactions")
    
    # Verify no transactions remain in old category
    print("Verifying category is empty...")
    all_transactions = client.transactions.list_transactions(user_id)
    remaining_transactions = [
        tx for tx in all_transactions 
        if tx.category and tx.category.id == old_category_id
    ]
    
    if remaining_transactions:
        print(f"WARNING: {len(remaining_transactions)} transactions still in old category!")
        return False
    
    # Delete old category
    print(f"Deleting old category {old_category_id}...")
    try:
        client.categories.delete_category(old_category_id)
        progress["processed_categories"].append(old_category_id)
        save_progress(progress)
        print("Category deleted successfully")
        return True
    except Exception as e:
        print(f"ERROR deleting category: {e}")
        return False


def main():
    # Get API key
    api_key = os.getenv('POCKETSMITH_API_KEY')
    if not api_key:
        print("Error: POCKETSMITH_API_KEY environment variable not set")
        print("Please set it with: export POCKETSMITH_API_KEY='your_api_key_here'")
        sys.exit(1)
    
    # Initialize client
    client = PocketsmithClient(api_key)
    
    try:
        # Get user info
        user_info = client.users.get_me()
        user_id = user_info['id']
        print(f"Processing categories for user: {user_info.get('email', 'Unknown')}")
        
        # Load progress
        progress = load_progress()
        if not progress["start_time"]:
            progress["start_time"] = datetime.now().isoformat()
        
        print(f"\nProgress: {len(progress['processed_categories'])}/{len(CATEGORY_MAPPING)} categories completed")
        print(f"Processed transactions: {len(progress['processed_transactions'])}")
        
        # Process each category
        for old_category_id, mapping in CATEGORY_MAPPING.items():
            if old_category_id in progress["processed_categories"]:
                print(f"Skipping already processed category {old_category_id}")
                continue
            
            progress["current_category"] = old_category_id
            save_progress(progress)
            
            success = process_category(client, user_id, old_category_id, mapping, progress)
            if not success:
                print(f"Failed to process category {old_category_id}. Stopping.")
                break
            
            print(f"Category {old_category_id} completed successfully")
        
        # Final summary
        if len(progress["processed_categories"]) == len(CATEGORY_MAPPING):
            print("\n🎉 ALL CATEGORIES PROCESSED SUCCESSFULLY!")
            print(f"Total transactions processed: {len(progress['processed_transactions'])}")
            print(f"Created categories: {list(progress['created_categories'].keys())}")
            
            # Verify final state
            print("\nVerifying final category count...")
            categories = client.categories.list_categories(user_id)
            print(f"Total categories remaining: {len(categories)}")
            for cat in categories:
                print(f"  - {cat.title} (ID: {cat.id})")
        else:
            print(f"\nProcess incomplete: {len(progress['processed_categories'])}/{len(CATEGORY_MAPPING)} categories")
            print("Run the script again to continue from where it left off")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()