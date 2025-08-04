#!/usr/bin/env python3
"""
PocketSmith Category Investigation Script

This script fetches sample transactions from specific category IDs to understand
why these transactions weren't remapped during the recategorization process.

Usage:
    export POCKETSMITH_API_KEY='your_api_key_here'
    uv run python investigate_categories.py
"""

import os
import sys
import json
import requests
from datetime import datetime
from pocketsmith import PocketsmithClient

# Categories to investigate (from user's list)
CATEGORIES_TO_INVESTIGATE = {
    7312544: {"name": "Eating out", "count": 53},
    7312589: {"name": "Inter-account", "count": 37},
    7312595: {"name": "Public transport", "count": 15},
    7280188: {"name": "Groceries", "count": 15},
    7312572: {"name": "Medical", "count": 11},
    7312546: {"name": "Coffee", "count": 11},
    7312577: {"name": "Mortgage", "count": 10},
    7312562: {"name": "Self-care", "count": 7},
    7280166: {"name": "Insurance", "count": 7},
    7314164: {"name": "Entertainment", "count": 7},
}

# Import the category mapping to check if these should be remapped
try:
    from category_mapping import CATEGORY_MAPPING
except ImportError:
    print("Warning: Could not import category mapping")
    CATEGORY_MAPPING = {}


def get_transactions_for_category(client, user_id, category_id, limit=3):
    """Get sample transactions for a specific category"""
    try:
        api_key = client.api_client.configuration.api_key['developerKey']
        url = f"https://api.pocketsmith.com/v2/users/{user_id}/transactions"
        headers = {
            "accept": "application/json",
            "X-Developer-Key": api_key
        }
        
        # First try with category_id parameter
        params = {
            'category_id': category_id,
            'per_page': limit,
            'page': 1
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 400:
            # If 400 error, try fetching more transactions and filter manually
            print(f"  ⚠️  Direct category filter failed, searching in recent transactions...")
            matching_transactions = []
            
            # Search through multiple pages if needed
            for page in range(1, 4):  # Search first 3 pages (up to 1500 transactions)
                params = {
                    'per_page': 500,
                    'page': page
                }
                
                page_response = requests.get(url, headers=headers, params=params)
                page_response.raise_for_status()
                
                page_transactions = page_response.json()
                if not page_transactions:
                    break  # No more transactions
                
                for transaction in page_transactions:
                    category = transaction.get('category', {})
                    if isinstance(category, dict) and category.get('id') == category_id:
                        matching_transactions.append(transaction)
                        if len(matching_transactions) >= limit:
                            return matching_transactions
                
                # If we found some transactions and this is the first page, 
                # show progress
                if page == 1 and matching_transactions:
                    print(f"    Found {len(matching_transactions)} transaction(s) so far...")
            
            return matching_transactions
        
        response.raise_for_status()
        transactions = response.json()
        return transactions
        
    except Exception as e:
        print(f"  ❌ Error fetching transactions for category {category_id}: {e}")
        return []


def format_transaction_details(transaction):
    """Format transaction details for display"""
    # Handle both dict and object formats
    if isinstance(transaction, dict):
        tx_id = transaction.get('id')
        payee = transaction.get('payee', 'Unknown')
        amount = transaction.get('amount', 0)
        date = transaction.get('date', 'Unknown')
        category = transaction.get('category', {})
        labels = transaction.get('labels', [])
        is_transfer = transaction.get('is_transfer', False)
    else:
        tx_id = getattr(transaction, 'id', None)
        payee = getattr(transaction, 'payee', 'Unknown')
        amount = getattr(transaction, 'amount', 0)
        date = getattr(transaction, 'date', 'Unknown')
        category = getattr(transaction, 'category', {})
        labels = getattr(transaction, 'labels', [])
        is_transfer = getattr(transaction, 'is_transfer', False)
    
    # Extract category info
    if isinstance(category, dict):
        cat_id = category.get('id')
        cat_title = category.get('title', 'Unknown')
    else:
        cat_id = getattr(category, 'id', None) if category else None
        cat_title = getattr(category, 'title', 'Unknown') if category else 'Unknown'
    
    # Format amount with proper sign
    amount_str = f"${abs(float(amount)):.2f}"
    if float(amount) < 0:
        amount_str = f"-{amount_str}"
    else:
        amount_str = f"+{amount_str}"
    
    # Format labels
    labels_str = f" [Labels: {', '.join(labels)}]" if labels else ""
    
    # Check if this is a transfer
    transfer_str = " [TRANSFER]" if is_transfer else ""
    
    return f"    • ID: {tx_id} | {payee[:40]:<40} | {amount_str:>10} | {date} | Cat: {cat_title} ({cat_id}){labels_str}{transfer_str}"


def check_mapping_status(category_id):
    """Check if this category should be remapped according to our mapping"""
    if category_id in CATEGORY_MAPPING:
        mapping = CATEGORY_MAPPING[category_id]
        return f"Should map to: {mapping['new_category']}" + (f" +{mapping['label']}" if mapping['label'] else "")
    else:
        return "❌ NOT IN MAPPING - This explains why it wasn't remapped!"


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
        print(f"Investigating categories for user: {user_info.get('email', 'Unknown')}")
        print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "="*100)
        print("CATEGORY INVESTIGATION REPORT")
        print("="*100)
        
        total_transactions_found = 0
        
        for category_id, info in CATEGORIES_TO_INVESTIGATE.items():
            print(f"\n📁 Category: {info['name']} (ID: {category_id}) - Expected {info['count']} transactions")
            print("-" * 80)
            
            # Check mapping status
            mapping_status = check_mapping_status(category_id)
            print(f"  Mapping Status: {mapping_status}")
            
            # Fetch sample transactions
            print(f"  Fetching sample transactions...")
            transactions = get_transactions_for_category(client, user_id, category_id, limit=3)
            
            if not transactions:
                print(f"  ⚠️  No transactions found for this category!")
                print(f"  💡 This suggests all transactions may have already been remapped or deleted.")
                continue
            
            total_transactions_found += len(transactions)
            print(f"  Found {len(transactions)} sample transaction(s):")
            
            for i, transaction in enumerate(transactions, 1):
                print(format_transaction_details(transaction))
            
            # Check if any have underscore-prefixed categories (our new categories)
            remapped_count = 0
            for transaction in transactions:
                if isinstance(transaction, dict):
                    category = transaction.get('category', {})
                    cat_title = category.get('title', '') if isinstance(category, dict) else ''
                else:
                    category = getattr(transaction, 'category', None)
                    cat_title = getattr(category, 'title', '') if category else ''
                
                if cat_title and cat_title.startswith('_'):
                    remapped_count += 1
            
            if remapped_count > 0:
                print(f"  ✅ {remapped_count}/{len(transactions)} sample transactions already have new categories")
            else:
                print(f"  ⚠️  None of the sample transactions have been remapped yet")
        
        print("\n" + "="*100)
        print("INVESTIGATION SUMMARY")
        print("="*100)
        print(f"Total sample transactions found: {total_transactions_found}")
        print(f"Categories investigated: {len(CATEGORIES_TO_INVESTIGATE)}")
        
        # Count how many categories are in our mapping
        mapped_categories = [cat_id for cat_id in CATEGORIES_TO_INVESTIGATE.keys() if cat_id in CATEGORY_MAPPING]
        unmapped_categories = [cat_id for cat_id in CATEGORIES_TO_INVESTIGATE.keys() if cat_id not in CATEGORY_MAPPING]
        
        print(f"Categories in mapping: {len(mapped_categories)}")
        print(f"Categories NOT in mapping: {len(unmapped_categories)}")
        
        if unmapped_categories:
            print(f"\n❌ Categories NOT in mapping (this explains why they weren't remapped):")
            for cat_id in unmapped_categories:
                info = CATEGORIES_TO_INVESTIGATE[cat_id]
                print(f"  • {cat_id}: {info['name']} ({info['count']} transactions)")
        
        if mapped_categories:
            print(f"\n✅ Categories that ARE in mapping (should have been remapped):")
            for cat_id in mapped_categories:
                info = CATEGORIES_TO_INVESTIGATE[cat_id]
                mapping = CATEGORY_MAPPING[cat_id]
                label_str = f" +{mapping['label']}" if mapping['label'] else ""
                print(f"  • {cat_id}: {info['name']} -> {mapping['new_category']}{label_str} ({info['count']} transactions)")
        
        # Check if we have recategorization progress
        progress_info = ""
        try:
            with open("recategorise_progress.json", 'r') as f:
                progress = json.load(f)
                if progress.get("completed"):
                    end_time = progress.get("end_time", "Unknown")
                    total_processed = progress.get("total_transactions_processed", 0)
                    total_remapped = progress.get("total_transactions_remapped", 0)
                    progress_info = f"\n📊 RECATEGORIZATION STATUS:"
                    progress_info += f"\n  ✅ Recategorization completed at: {end_time}"
                    progress_info += f"\n  📈 Processed: {total_processed} transactions, Remapped: {total_remapped} transactions"
                    
                    # Check if our found transactions are newer than the completion time
                    if total_transactions_found > 0:
                        progress_info += f"\n  💡 The {total_transactions_found} transactions found are likely NEW transactions"
                        progress_info += f"\n     that came in after recategorization completed."
                else:
                    progress_info = f"\n⚠️  RECATEGORIZATION STATUS: Not completed yet"
        except FileNotFoundError:
            progress_info = f"\n⚠️  No recategorization progress file found"
        except Exception as e:
            progress_info = f"\n⚠️  Error reading progress: {e}"
        
        print(progress_info)
        
        print(f"\n💡 RECOMMENDATIONS:")
        if unmapped_categories:
            print(f"  1. Add missing categories to category_mapping.py if they should be remapped")
            print(f"  2. Run the recategorization script again to process these categories")
        if mapped_categories and total_transactions_found == 0:
            print(f"  3. ✅ Great! All transactions appear to have been successfully remapped")
            print(f"     The old categories are empty, indicating successful migration")
        elif mapped_categories and total_transactions_found > 0:
            print(f"  3. The {total_transactions_found} remaining transactions are likely:")
            print(f"     • New transactions that came in after recategorization completed")
            print(f"     • Run recategorization again to catch these new transactions:")
            print(f"       uv run python recategorise.py")
            print(f"     • Or set up a scheduled job to handle new transactions regularly")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()