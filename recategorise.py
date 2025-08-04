#!/usr/bin/env python3
"""
PocketSmith Category Recategorisation Script

This script consolidates 63 existing categories down to 12 new categories,
using labels to retain granular information.

Usage:
    export POCKETSMITH_API_KEY='your_api_key_here'
    python recategorise.py [--test-limit N]  # Test mode with N transactions
    python cleanup_categories.py             # Cleanup empty old categories
"""

import os
import sys
import json
import time
import argparse
import re
from datetime import datetime
from pocketsmith import PocketsmithClient

# Import shared category mapping
from category_mapping import CATEGORY_MAPPING

PROGRESS_FILE = "recategorise_progress.json"


def load_progress():
    """Load progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        "start_time": None,
        "end_time": None,
        "last_processed_page": 0,
        "last_processed_transaction_id": 0,
        "processed_transactions": [],
        "created_categories": {},
        "total_transactions_processed": 0,
        "total_transactions_remapped": 0,
        "unmapped_transactions": [],  # Transaction IDs that couldn't be remapped
        "uncategorized_transactions": [],  # Transaction IDs with no category
        "completed": False
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
    
    # Check if we can reuse an existing category with underscore prefix (from previous runs)
    # Only reuse categories we've created (with underscore prefix), not original data categories
    categories = client.categories.list_categories(user_id)
    target_name = f"_{category_name}"
    for cat in categories:
        if cat.title == target_name:
            print(f"Found existing new category: {cat.title} (ID: {cat.id})")
            progress["created_categories"][category_name] = cat.id
            save_progress(progress)
            return cat.id
    
    # Create new category using requests (based on API documentation)
    print(f"Creating new category: {category_name}")
    try:
        import requests
        
        # Use direct requests call as shown in PocketSmith documentation
        url = f"https://api.pocketsmith.com/v2/users/{user_id}/categories"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Developer-Key": client.api_client.configuration.api_key['developerKey']
        }
        # Add underscore prefix to avoid conflicts with existing categories
        unique_name = f"_{category_name}"
        data = {"title": unique_name}
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 201:  # Not created
            error_details = response.text
            raise Exception(f"HTTP {response.status_code}: {error_details}")
        response.raise_for_status()
        
        category_data = response.json()
        category_id = category_data['id']
        print(f"✅ Created category: {unique_name} (ID: {category_id})")
        
    except Exception as e:
        print(f"❌ Error creating category: {e}")
        # For now, skip this transaction - we'll handle this better later
        return None
    
    progress["created_categories"][category_name] = category_id
    save_progress(progress)
    return category_id


def parse_link_header(link_header):
    """Parse Link header to extract next/prev URLs"""
    if not link_header:
        return {}
    
    links = {}
    for link in link_header.split(','):
        link = link.strip()
        if '; rel=' in link:
            url_part, rel_part = link.split('; rel=', 1)
            url = url_part.strip('<>')
            rel = rel_part.strip('"')
            links[rel] = url
    return links


def get_transactions_page(client, user_id, page=1, per_page=1000):
    """Get a page of transactions using pagination"""
    try:
        # Use direct requests call since the underlying API client auth isn't working
        import requests
        
        api_key = client.api_client.configuration.api_key['developerKey']
        url = f"https://api.pocketsmith.com/v2/users/{user_id}/transactions"
        headers = {
            "accept": "application/json",
            "X-Developer-Key": api_key
        }
        params = {'page': page, 'per_page': per_page}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        transactions_data = response.json()
        
        # Convert to transaction objects manually - for now just return raw data
        # The processing code will need to handle both dict and object formats
        link_header = response.headers.get('Link', '')
        links = parse_link_header(link_header)
        
        return transactions_data, links
        
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        # Fallback to basic method without pagination
        if page == 1:
            transactions = client.transactions.list_transactions(user_id)
            return transactions, {}
        else:
            return [], {}


def is_transaction_processed(transaction_id, processed_transactions):
    """Check if transaction is already processed using optimized search"""
    # Convert to set for O(1) lookup if list is large
    if len(processed_transactions) > 100:
        # Use set for large lists - convert once and cache
        if not hasattr(is_transaction_processed, '_processed_set'):
            is_transaction_processed._processed_set = set(processed_transactions)
        return transaction_id in is_transaction_processed._processed_set
    
    # For small lists, use the optimized linear search
    # processed_transactions is in ascending order
    for processed_id in processed_transactions:
        if processed_id == transaction_id:
            return True
        elif processed_id > transaction_id:
            # Since list is in ascending order, we can stop searching
            break
    return False


def process_transaction(client, user_id, transaction, progress):
    """Process a single transaction for remapping"""
    # Handle both dict and object formats for transaction
    if isinstance(transaction, dict):
        transaction_id = transaction['id']
        transaction_payee = transaction['payee']
        transaction_amount = transaction['amount']
        transaction_date = transaction['date']
        transaction_category = transaction.get('category')
        transaction_labels = transaction.get('labels', [])
    else:
        transaction_id = transaction.id
        transaction_payee = transaction.payee
        transaction_amount = transaction.amount
        transaction_date = transaction.date
        transaction_category = transaction.category
        transaction_labels = transaction.labels
    
    # Skip if already processed using optimized check
    if is_transaction_processed(transaction_id, progress["processed_transactions"]):
        return False, "already_processed"
    
    # Check if transaction needs remapping
    # Handle both dict and object formats for category
    if transaction_category:
        if isinstance(transaction_category, dict):
            category_id = transaction_category.get('id')
            category_title = transaction_category.get('title')
        elif hasattr(transaction_category, 'id'):
            category_id = transaction_category.id
            category_title = transaction_category.title
        else:
            category_id = None
            category_title = None
    else:
        category_id = None
        category_title = None
    
    if not transaction_category:
        # Transaction has no category - record ID only
        if transaction_id not in progress["uncategorized_transactions"]:
            progress["uncategorized_transactions"].append(transaction_id)
        # Add to processed list (will be sorted later for efficiency)
        progress["processed_transactions"].append(transaction_id)
        # Invalidate cached set
        if hasattr(is_transaction_processed, '_processed_set'):
            delattr(is_transaction_processed, '_processed_set')
        return False, "uncategorized"
    
    # Skip transactions that already have underscore-prefixed categories (our new categories)
    if category_title and category_title.startswith('_'):
        # Transaction already has a new category - skip it
        progress["processed_transactions"].append(transaction_id)
        # Invalidate cached set
        if hasattr(is_transaction_processed, '_processed_set'):
            delattr(is_transaction_processed, '_processed_set')
        return False, "already_remapped"
    
    if category_id not in CATEGORY_MAPPING:
        # Category not in mapping - record ID only
        if transaction_id not in progress["unmapped_transactions"]:
            progress["unmapped_transactions"].append(transaction_id)
        # Add to processed list (will be sorted later for efficiency)
        progress["processed_transactions"].append(transaction_id)
        # Invalidate cached set
        if hasattr(is_transaction_processed, '_processed_set'):
            delattr(is_transaction_processed, '_processed_set')
        return False, "unmapped_category"
    
    old_category_id = category_id
    mapping = CATEGORY_MAPPING[old_category_id]
    new_category_name = mapping["new_category"]
    label = mapping["label"]
    
    try:
        # Get or create new category
        new_category_id = get_or_create_category(client, user_id, new_category_name, progress)
        
        if new_category_id is None:
            # Category creation failed - record as unmapped
            if transaction_id not in progress["unmapped_transactions"]:
                progress["unmapped_transactions"].append(transaction_id)
            # Add to processed list (will be sorted later for efficiency)
            progress["processed_transactions"].append(transaction_id)
            # Invalidate cached set
            if hasattr(is_transaction_processed, '_processed_set'):
                delattr(is_transaction_processed, '_processed_set')
            return False, "category_creation_failed"
        
        # Prepare update data
        update_data = {"category_id": new_category_id}
        
        # Add label if specified
        if label:
            current_labels = list(transaction_labels) if transaction_labels else []
            if label not in current_labels:
                current_labels.append(label)
            update_data["labels"] = current_labels
        
        # Update transaction using direct REST API
        print(f"  Remapping transaction {transaction_id}: {transaction_payee[:50]} | {category_title} -> {new_category_name}" + (f" +{label}" if label else ""))
        
        import requests
        url = f"https://api.pocketsmith.com/v2/transactions/{transaction_id}"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Developer-Key": client.api_client.configuration.api_key['developerKey']
        }
        
        response = requests.put(url, headers=headers, json=update_data)
        if response.status_code not in [200, 204]:  # Success codes for PUT
            error_details = response.text
            raise Exception(f"HTTP {response.status_code}: {error_details}")
        response.raise_for_status()
        
        # Mark as processed - append for efficiency (will be sorted later)
        progress["processed_transactions"].append(transaction_id)
        # Invalidate cached set
        if hasattr(is_transaction_processed, '_processed_set'):
            delattr(is_transaction_processed, '_processed_set')
        progress["total_transactions_remapped"] += 1
        
        # Rate limiting
        time.sleep(0.1)
        
        return True, "remapped"
        
    except Exception as e:
        print(f"  ERROR updating transaction {transaction_id}: {e}")
        return False, f"error: {e}"




def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Recategorise PocketSmith transactions')
    parser.add_argument('--test-limit', type=int, help='Test mode: limit processing to N transactions')
    args = parser.parse_args()
    
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
        print(f"Processing transactions for user: {user_info.get('email', 'Unknown')}")
        
        # Load progress
        progress = load_progress()
        if not progress["start_time"]:
            progress["start_time"] = datetime.now().isoformat()
        
        print(f"\nProgress: Processed {progress['total_transactions_processed']} transactions")
        print(f"Remapped: {progress['total_transactions_remapped']} transactions")
        print(f"Unmapped: {len(progress.get('unmapped_transactions', []))} transactions")
        print(f"Uncategorized: {len(progress.get('uncategorized_transactions', []))} transactions")
        print(f"Last processed page: {progress['last_processed_page']}")
        print(f"Created categories: {list(progress['created_categories'].keys())}")
        
        if args.test_limit:
            print(f"\n🧪 TEST MODE: Processing up to {args.test_limit} transactions")
        
        # Start pagination from where we left off
        page = max(1, progress["last_processed_page"])
        transactions_processed_this_run = 0
        transactions_remapped_this_run = 0
        
        while True:
            print(f"\nFetching page {page}...")
            transactions, links = get_transactions_page(client, user_id, page, per_page=1000)
            
            if not transactions:
                print("No more transactions found")
                break
            
            print(f"Processing {len(transactions)} transactions from page {page}")
            
            # Sort transactions by ID in descending order (newest first)
            if transactions and isinstance(transactions[0], dict):
                transactions.sort(key=lambda t: t['id'], reverse=True)
            else:
                transactions.sort(key=lambda t: t.id, reverse=True)
            
            page_remapped = 0
            for transaction in transactions:
                
                progress["total_transactions_processed"] += 1
                transactions_processed_this_run += 1
                
                # Process the transaction
                remapped, status = process_transaction(client, user_id, transaction, progress)
                if remapped:
                    page_remapped += 1
                    transactions_remapped_this_run += 1
                
                # Update last processed transaction ID for resume capability
                if isinstance(transaction, dict):
                    current_id = transaction['id']
                else:
                    current_id = transaction.id
                progress["last_processed_transaction_id"] = min(
                    progress["last_processed_transaction_id"], 
                    current_id
                )
                            
                # Test mode limit
                if args.test_limit and transactions_processed_this_run >= args.test_limit:
                    print(f"\n🧪 TEST LIMIT REACHED: Processed {transactions_processed_this_run} transactions")
                    break
            
            # Sort processed transactions for optimal search performance
            progress["processed_transactions"].sort()
            
            # Update progress and save once per page
            progress["last_processed_page"] = page
            save_progress(progress)
            
            print(f"Page {page} complete: {page_remapped} transactions remapped")
            
            # Test mode limit reached
            if args.test_limit and transactions_processed_this_run >= args.test_limit:
                break
            
            # Check if there's a next page
            if 'next' not in links:
                print("Reached last page of transactions")
                break
            
            page += 1
        
        # Mark as completed if not in test mode
        if not args.test_limit:
            progress["completed"] = True
            progress["end_time"] = datetime.now().isoformat()
        
        save_progress(progress)
        
        # Final summary
        print(f"\n{'🧪 TEST MODE ' if args.test_limit else '🎉 '}PROCESSING COMPLETE!")
        print(f"Transactions processed this run: {transactions_processed_this_run}")
        print(f"Transactions remapped this run: {transactions_remapped_this_run}")
        print(f"Total transactions processed: {progress['total_transactions_processed']}")
        print(f"Total transactions remapped: {progress['total_transactions_remapped']}")
        print(f"Unmapped transactions: {len(progress.get('unmapped_transactions', []))}")
        print(f"Uncategorized transactions: {len(progress.get('uncategorized_transactions', []))}")
        print(f"Created categories: {list(progress['created_categories'].keys())}")
        
        # Show details of unmapped transactions
        if progress.get('unmapped_transactions'):
            print(f"\n⚠️  Unmapped transaction IDs (category not in mapping):")
            unmapped_ids = progress['unmapped_transactions'][:5]  # Show first 5
            print(f"  - Transaction IDs: {', '.join(map(str, unmapped_ids))}")
            if len(progress['unmapped_transactions']) > 5:
                print(f"  ... and {len(progress['unmapped_transactions']) - 5} more")
        
        if progress.get('uncategorized_transactions'):
            print(f"\n⚠️  Uncategorized transaction IDs (no category assigned):")
            uncategorized_ids = progress['uncategorized_transactions'][:5]  # Show first 5
            print(f"  - Transaction IDs: {', '.join(map(str, uncategorized_ids))}")
            if len(progress['uncategorized_transactions']) > 5:
                print(f"  ... and {len(progress['uncategorized_transactions']) - 5} more")
        
        if not args.test_limit and progress["completed"]:
            print("\n✅ All transactions have been processed!")
            print("To delete old empty categories, run: python cleanup_categories.py")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
