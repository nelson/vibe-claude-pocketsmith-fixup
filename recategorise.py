#!/usr/bin/env python3
"""
PocketSmith Category Recategorisation Script

This script consolidates 63 existing categories down to 12 new categories,
using labels to retain granular information.

Usage:
    export POCKETSMITH_API_KEY='your_api_key_here'
    python recategorise.py [--test-limit N]  # Test mode with N transactions
    python recategorise.py --cleanup         # Cleanup empty old categories
"""

import os
import sys
import json
import time
import argparse
import re
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
    
    # Subcategories (children) - map to same as parent
    7312268: {"new_category": "Bills", "label": "utilities"},  # Electricity (child of Bills)
    7312269: {"new_category": "Bills", "label": "utilities"},  # Gas (child of Bills)
    7312270: {"new_category": "Bills", "label": "internet"},  # Internet (child of Bills)
    7312271: {"new_category": "Bills", "label": "subscription"},  # Media (child of Bills)
    7312272: {"new_category": "Bills", "label": "comms"},  # Mobile (child of Bills)
    7312273: {"new_category": "Bills", "label": "utilities"},  # Rates (child of Bills)
    7314701: {"new_category": "Income", "label": "tax"},  # Tax (child of Bills)
    7312274: {"new_category": "Bills", "label": "utilities"},  # Water (child of Bills)
    7312545: {"new_category": "Dining", "label": "restaurants"},  # Bubble tea (child of Eating out)
    7312546: {"new_category": "Dining", "label": "restaurants"},  # Coffee (child of Eating out)
    7312547: {"new_category": "Dining", "label": "takeout"},  # Fast food (child of Eating out)
    7312548: {"new_category": "Dining", "label": "restaurants"},  # Paying for others (child of Eating out)
    7312550: {"new_category": "Education", "label": "childcare"},  # Childcare (child of Education)
    7312551: {"new_category": "Education", "label": "classes"},  # Music (child of Education)
    7312552: {"new_category": "Education", "label": "classes"},  # School (child of Education)
    7312553: {"new_category": "Education", "label": "classes"},  # Tutoring (child of Education)
    7312555: {"new_category": "Giving", "label": "church"},  # Church (child of Giving)
    7280222: {"new_category": "Giving", "label": "charity"},  # Gifts (child of Giving)
    7312556: {"new_category": "Giving", "label": "missions"},  # Missionary (child of Giving)
    7312558: {"new_category": "Groceries", "label": "markets"},  # Asian stores (child of Groceries)
    7312559: {"new_category": "Groceries", "label": "markets"},  # Markets (child of Groceries)
    7312557: {"new_category": "Groceries", "label": "supermarkets"},  # Supermarket (child of Groceries)
    7312561: {"new_category": "Household", "label": "production"},  # Appliances (child of Household)
    7280205: {"new_category": "Household", "label": "cash"},  # Cash spend (child of Household)
    7312563: {"new_category": "Household", "label": "production"},  # Furniture (child of Household)
    7312564: {"new_category": "Household", "label": "maintenance"},  # Gardening (child of Household)
    7312565: {"new_category": "Household", "label": "maintenance"},  # Maintanence (child of Household)
    7312566: {"new_category": "Household", "label": "personal-care"},  # Occasions (child of Household)
    7312562: {"new_category": "Household", "label": "personal-care"},  # Self-care (child of Household)
    7312567: {"new_category": "Household", "label": "production"},  # Tools (child of Household)
    7666458: {"new_category": "Household", "label": "production"},  # Supplies (child of Household)
    7341096: {"new_category": "Income", "label": None},  # Expense Reimbursement (child of Income)
    7314702: {"new_category": "Income", "label": "investment"},  # Investment (child of Income)
    7314703: {"new_category": "Income", "label": "other-income"},  # Rental (child of Income)
    7314704: {"new_category": "Income", "label": "salary"},  # Salary (child of Income)
    7314705: {"new_category": "Income", "label": "superannuation"},  # Superannuation (child of Income)
    7312569: {"new_category": "Bills", "label": "medical"},  # Health (child of Insurance)
    7312570: {"new_category": "Bills", "label": "insurance"},  # Home (child of Insurance)
    7312571: {"new_category": "Transport", "label": "insurance"},  # Motor (child of Insurance)
    7312573: {"new_category": "Bills", "label": "medical"},  # Dental (child of Medical)
    7312574: {"new_category": "Bills", "label": "medical"},  # GP (child of Medical)
    7312575: {"new_category": "Bills", "label": "medical"},  # NDIS (child of Medical)
    7312576: {"new_category": "Bills", "label": "medical"},  # Optical (child of Medical)
    7312578: {"new_category": "Mortgage", "label": None},  # Equity (child of Mortgage)
    7312579: {"new_category": "Mortgage", "label": None},  # Interest (child of Mortgage)
    7312581: {"new_category": "Dining", "label": "restaurants"},  # Alcohol (child of Recreation)
    7312582: {"new_category": "Shopping", "label": "hobbies"},  # Books (child of Recreation)
    7314164: {"new_category": "Shopping", "label": "hobbies"},  # Entertainment (child of Recreation)
    7312583: {"new_category": "Shopping", "label": "hobbies"},  # Gadgets (child of Recreation)
    7312600: {"new_category": "Shopping", "label": "hobbies"},  # Games (child of Recreation)
    7312584: {"new_category": "Holidays", "label": None},  # Holidays (child of Recreation)
    7312585: {"new_category": "Holidays", "label": "hotels"},  # Hotels (child of Recreation)
    7312586: {"new_category": "Shopping", "label": "health"},  # Sports (child of Recreation)
    7280182: {"new_category": "Transfer", "label": None},  # Credit Card Payments (child of Transfer)
    7312589: {"new_category": "Transfer", "label": None},  # Inter-account (child of Transfer)
    7312588: {"new_category": "Transfer", "label": None},  # Loan payments (child of Transfer)
    7312591: {"new_category": "Transport", "label": "fines"},  # Fines (child of Transport)
    7312592: {"new_category": "Holidays", "label": "flights"},  # Flights (child of Transport)
    7312593: {"new_category": "Transport", "label": "parking"},  # Parking (child of Transport)
    7312594: {"new_category": "Transport", "label": "petrol"},  # Petrol (child of Transport)
    7312595: {"new_category": "Transport", "label": "public-transport"},  # Public transport (child of Transport)
    7312597: {"new_category": "Transport", "label": "car"},  # Registration (child of Transport)
    7312598: {"new_category": "Transport", "label": "car"},  # Servicing (child of Transport)
    7707848: {"new_category": "Transport", "label": "car"},  # Taxi (child of Transport)
    7312596: {"new_category": "Transport", "label": "tolls"},  # Tolls (child of Transport)
}

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
        "unmapped_transactions": [],  # Transactions that couldn't be remapped
        "uncategorized_transactions": [],  # Transactions with no category
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
        # The list_transactions method might not support pagination parameters directly
        # We'll need to use the underlying API client
        response = client.api_client.call_api(
            '/users/{id}/transactions',
            'GET',
            path_params={'id': user_id},
            query_params={'page': page, 'per_page': per_page},
            header_params={},
            body=None,
            post_params=[],
            files={},
            response_type='list[Transaction]',
            auth_settings=['developers'],
            async_req=False,
            _return_http_data_only=False
        )
        
        transactions = response[0]  # The actual data
        headers = response[2]  # Response headers
        link_header = headers.get('Link', '')
        links = parse_link_header(link_header)
        
        return transactions, links
        
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        # Fallback to basic method without pagination
        if page == 1:
            transactions = client.transactions.list_transactions(user_id)
            return transactions, {}
        else:
            return [], {}


def process_transaction(client, user_id, transaction, progress):
    """Process a single transaction for remapping"""
    # Skip if already processed
    if transaction.id in progress["processed_transactions"]:
        return False, "already_processed"
    
    # Check if transaction needs remapping
    # Handle both dict and object formats for category
    if hasattr(transaction.category, 'id'):
        category_id = transaction.category.id
        category_title = transaction.category.title
    elif isinstance(transaction.category, dict):
        category_id = transaction.category.get('id')
        category_title = transaction.category.get('title')
    else:
        category_id = None
        category_title = None
    
    if not transaction.category:
        # Transaction has no category - record it
        uncategorized_info = {
            "id": transaction.id,
            "payee": transaction.payee,
            "amount": transaction.amount,
            "date": str(transaction.date) if hasattr(transaction.date, 'isoformat') else str(transaction.date)
        }
        if uncategorized_info not in progress["uncategorized_transactions"]:
            progress["uncategorized_transactions"].append(uncategorized_info)
        progress["processed_transactions"].append(transaction.id)
        return False, "uncategorized"
    
    if category_id not in CATEGORY_MAPPING:
        # Category not in mapping - record it for later review
        unmapped_info = {
            "id": transaction.id,
            "payee": transaction.payee,
            "amount": transaction.amount,
            "date": str(transaction.date) if hasattr(transaction.date, 'isoformat') else str(transaction.date),
            "category_id": category_id,
            "category_title": category_title
        }
        if unmapped_info not in progress["unmapped_transactions"]:
            progress["unmapped_transactions"].append(unmapped_info)
        progress["processed_transactions"].append(transaction.id)
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
            unmapped_info = {
                "id": transaction.id,
                "payee": transaction.payee,
                "amount": transaction.amount,
                "date": str(transaction.date) if hasattr(transaction.date, 'isoformat') else str(transaction.date),
                "category_id": old_category_id,
                "category_title": category_title,
                "error": "category_creation_failed"
            }
            if unmapped_info not in progress["unmapped_transactions"]:
                progress["unmapped_transactions"].append(unmapped_info)
            progress["processed_transactions"].append(transaction.id)
            return False, "category_creation_failed"
        
        # Prepare update data
        update_data = {"category_id": new_category_id}
        
        # Add label if specified
        if label:
            current_labels = list(transaction.labels) if transaction.labels else []
            if label not in current_labels:
                current_labels.append(label)
            update_data["labels"] = current_labels
        
        # Update transaction using direct REST API
        print(f"  Remapping transaction {transaction.id}: {transaction.payee[:50]} | {category_title} -> {new_category_name}" + (f" +{label}" if label else ""))
        
        import requests
        url = f"https://api.pocketsmith.com/v2/transactions/{transaction.id}"
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
        
        # Mark as processed
        progress["processed_transactions"].append(transaction.id)
        progress["total_transactions_remapped"] += 1
        
        # Rate limiting
        time.sleep(0.1)
        
        return True, "remapped"
        
    except Exception as e:
        print(f"  ERROR updating transaction {transaction.id}: {e}")
        return False, f"error: {e}"


def cleanup_old_categories(client, user_id):
    """Delete all old categories after verifying they're empty"""
    print("\n=== CLEANUP: Deleting old empty categories ===")
    
    # Get all current transactions to verify categories are empty
    print("Loading all transactions to verify old categories are empty...")
    all_transactions = client.transactions.list_transactions(user_id)
    
    deleted_count = 0
    for old_category_id in CATEGORY_MAPPING.keys():
        # Check if any transactions still use this category
        remaining_transactions = [
            tx for tx in all_transactions 
            if tx.category and tx.category.id == old_category_id
        ]
        
        if remaining_transactions:
            print(f"WARNING: Category {old_category_id} still has {len(remaining_transactions)} transactions - skipping deletion")
            continue
        
        try:
            print(f"Deleting old category {old_category_id}...")
            client.categories.delete_category(old_category_id)
            deleted_count += 1
        except Exception as e:
            print(f"ERROR deleting category {old_category_id}: {e}")
    
    print(f"Deleted {deleted_count}/{len(CATEGORY_MAPPING)} old categories")
    return deleted_count


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Recategorise PocketSmith transactions')
    parser.add_argument('--test-limit', type=int, help='Test mode: limit processing to N transactions')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup mode: delete empty old categories')
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
        
        # Cleanup mode
        if args.cleanup:
            cleanup_old_categories(client, user_id)
            return
        
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
            
            page_remapped = 0
            for transaction in transactions:
                # Skip transactions we've already processed (based on ID)
                if transaction.id <= progress["last_processed_transaction_id"]:
                    continue
                
                progress["total_transactions_processed"] += 1
                transactions_processed_this_run += 1
                
                # Process the transaction
                remapped, status = process_transaction(client, user_id, transaction, progress)
                if remapped:
                    page_remapped += 1
                    transactions_remapped_this_run += 1
                
                # Update last processed transaction ID
                progress["last_processed_transaction_id"] = max(
                    progress["last_processed_transaction_id"], 
                    transaction.id
                )
                
                # Test mode limit
                if args.test_limit and transactions_processed_this_run >= args.test_limit:
                    print(f"\n🧪 TEST LIMIT REACHED: Processed {transactions_processed_this_run} transactions")
                    break
            
            # Update progress
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
            print(f"\n⚠️  Unmapped transactions (category not in mapping):")
            for tx in progress['unmapped_transactions'][:5]:  # Show first 5
                print(f"  - {tx['payee'][:40]}... | Category: {tx['category_title']} (ID: {tx['category_id']})")
            if len(progress['unmapped_transactions']) > 5:
                print(f"  ... and {len(progress['unmapped_transactions']) - 5} more")
        
        if progress.get('uncategorized_transactions'):
            print(f"\n⚠️  Uncategorized transactions (no category assigned):")
            for tx in progress['uncategorized_transactions'][:5]:  # Show first 5
                print(f"  - {tx['payee'][:40]}... | Amount: {tx['amount']}")
            if len(progress['uncategorized_transactions']) > 5:
                print(f"  ... and {len(progress['uncategorized_transactions']) - 5} more")
        
        if not args.test_limit and progress["completed"]:
            print("\n✅ All transactions have been processed!")
            print("To delete old empty categories, run: python recategorise.py --cleanup")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()