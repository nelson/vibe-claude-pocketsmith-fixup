#!/usr/bin/env python3
"""
PocketSmith Category Cleanup Tool

This script cleans up old, empty categories after the recategorization process.
It safely identifies and deletes categories that are no longer in use, while
preserving categories that begin with underscore (our new categories).

Features:
- Paginated transaction fetching for efficient processing
- Comprehensive category usage analysis
- Safe deletion with multiple verification steps
- Progress tracking with timestamped snapshots
- Never deletes underscore-prefixed categories
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from collections import defaultdict

import requests
from pocketsmith import PocketsmithClient

# Import shared category mapping
from category_mapping import CATEGORY_MAPPING


def load_progress():
    """Load existing cleanup progress from JSON file"""
    progress_file = "cleanup_progress.json"
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load progress file: {e}")
    
    # Return empty progress structure
    return {
        "snapshots": [],
        "deleted_categories": [],
        "last_updated": None
    }


def save_progress(progress):
    """Save cleanup progress to JSON file"""
    progress["last_updated"] = datetime.now().isoformat()
    try:
        with open("cleanup_progress.json", 'w') as f:
            json.dump(progress, f, indent=2, default=str)
    except Exception as e:
        print(f"Warning: Could not save progress: {e}")


def parse_link_header(link_header):
    """Parse pagination links from Link header"""
    links = {}
    if link_header:
        for link in link_header.split(','):
            parts = link.strip().split(';')
            if len(parts) == 2:
                url = parts[0].strip('<>')
                rel = parts[1].split('=')[1].strip('"')
                links[rel] = url
    return links


def get_transactions_page(client, user_id, page=1, per_page=1000):
    """Get a page of transactions using direct API calls"""
    try:
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
        link_header = response.headers.get('Link', '')
        links = parse_link_header(link_header)
        
        return transactions_data, links
        
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        return [], {}


def get_all_categories(client, user_id):
    """Get all categories for the user"""
    try:
        categories = client.categories.list_categories(user_id)
        return categories
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []


def delete_category(client, category_id):
    """Delete a category using direct API call"""
    try:
        api_key = client.api_client.configuration.api_key['developerKey']
        url = f"https://api.pocketsmith.com/v2/categories/{category_id}"
        headers = {
            "accept": "application/json",
            "X-Developer-Key": api_key
        }
        
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True
        
    except Exception as e:
        print(f"Error deleting category {category_id}: {e}")
        return False


def analyze_category_usage(client, user_id):
    """Analyze category usage across all transactions"""
    print("=== ANALYZING CATEGORY USAGE ===")
    print("Fetching all transactions to analyze category usage...")
    
    category_counts = defaultdict(int)
    category_details = {}
    transaction_count = 0
    page = 1
    
    # Fetch all categories first to get their details
    all_categories = get_all_categories(client, user_id)
    for category in all_categories:
        if hasattr(category, 'id'):
            category_details[category.id] = {
                'id': category.id,
                'title': category.title,
                'is_transfer': getattr(category, 'is_transfer', False)
            }
    
    # Process all transactions page by page
    while True:
        print(f"Fetching page {page}...")
        transactions, links = get_transactions_page(client, user_id, page)
        
        if not transactions:
            print("No more transactions found")
            break
        
        # Count category usage in this page
        for transaction in transactions:
            transaction_count += 1
            category = transaction.get('category')
            if category and isinstance(category, dict):
                category_id = category.get('id')
                if category_id:
                    category_counts[category_id] += 1
                    # Store category details if we don't have them
                    if category_id not in category_details:
                        category_details[category_id] = {
                            'id': category_id,
                            'title': category.get('title', 'Unknown'),
                            'is_transfer': category.get('is_transfer', False)
                        }
        
        print(f"Page {page} complete: processed {len(transactions)} transactions")
        
        # Check if there are more pages
        if 'next' not in links:
            print("Reached last page of transactions")
            break
        
        page += 1
        time.sleep(0.1)  # Rate limiting
    
    print(f"Analysis complete: {transaction_count} total transactions processed")
    print(f"Found {len(category_counts)} categories in use")
    
    return category_counts, category_details


def cleanup_old_categories(client, user_id, dry_run=False):
    """Clean up old empty categories after verification"""
    print("\n=== CATEGORY CLEANUP ===")
    
    # Load existing progress
    progress = load_progress()
    
    # Analyze current category usage
    category_counts, category_details = analyze_category_usage(client, user_id)
    
    # Create snapshot of current state
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "total_transactions_analyzed": sum(category_counts.values()),
        "categories_in_use": len(category_counts),
        "category_usage": {},
        "deletion_candidates": [],
        "protected_categories": []
    }
    
    # Analyze each category
    for category_id, details in category_details.items():
        usage_count = category_counts.get(category_id, 0)
        category_title = details['title']
        
        snapshot["category_usage"][str(category_id)] = {
            "id": category_id,
            "title": category_title,
            "transaction_count": usage_count,
            "is_transfer": details.get('is_transfer', False)
        }
        
        # Never delete underscore-prefixed categories (our new categories)
        if category_title.startswith('_'):
            snapshot["protected_categories"].append({
                "id": category_id,
                "title": category_title,
                "reason": "underscore_prefix",
                "transaction_count": usage_count
            })
            continue
        
        # Check if this is an old category we want to clean up
        if category_id in CATEGORY_MAPPING:
            if usage_count == 0:
                snapshot["deletion_candidates"].append({
                    "id": category_id,
                    "title": category_title,
                    "transaction_count": usage_count,
                    "mapped_to": CATEGORY_MAPPING[category_id]["new_category"]
                })
            else:
                print(f"WARNING: Old category '{category_title}' (ID: {category_id}) still has {usage_count} transactions")
    
    # Add snapshot to progress
    progress["snapshots"].append(snapshot)
    
    # Report findings
    print(f"\nCATEGORY ANALYSIS RESULTS:")
    print(f"- Total categories found: {len(category_details)}")
    print(f"- Categories with transactions: {len([c for c in category_counts.values() if c > 0])}")
    print(f"- Empty categories eligible for deletion: {len(snapshot['deletion_candidates'])}")
    print(f"- Protected categories (underscore prefix): {len(snapshot['protected_categories'])}")
    
    if snapshot["deletion_candidates"]:
        print(f"\nEMPTY CATEGORIES READY FOR DELETION:")
        for candidate in snapshot["deletion_candidates"]:
            print(f"  - {candidate['title']} (ID: {candidate['id']}) -> was mapped to {candidate['mapped_to']}")
    
    # Perform deletions if not in dry-run mode
    deleted_count = 0
    deletion_errors = []
    
    if not dry_run and snapshot["deletion_candidates"]:
        print(f"\nDeleting {len(snapshot['deletion_candidates'])} empty categories...")
        
        for candidate in snapshot["deletion_candidates"]:
            category_id = candidate['id']
            category_title = candidate['title']
            
            print(f"Deleting category '{category_title}' (ID: {category_id})...")
            if delete_category(client, category_id):
                progress["deleted_categories"].append({
                    "id": category_id,
                    "title": category_title,
                    "deleted_at": datetime.now().isoformat(),
                    "mapped_to": candidate['mapped_to']
                })
                deleted_count += 1
                time.sleep(0.5)  # Rate limiting for deletions
            else:
                deletion_errors.append({
                    "id": category_id,
                    "title": category_title,
                    "error": "API deletion failed"
                })
    
    # Update snapshot with deletion results
    snapshot["deletions_performed"] = deleted_count
    snapshot["deletion_errors"] = deletion_errors
    snapshot["dry_run"] = dry_run
    
    # Save progress
    save_progress(progress)
    
    print(f"\nCLEANUP COMPLETE:")
    if dry_run:
        print("✓ DRY RUN MODE - No categories were deleted")
        print(f"✓ Found {len(snapshot['deletion_candidates'])} categories ready for deletion")
    else:
        print(f"✓ Successfully deleted {deleted_count} empty categories")
        if deletion_errors:
            print(f"✗ Failed to delete {len(deletion_errors)} categories")
    
    print(f"✓ Progress saved to cleanup_progress.json")
    print(f"✓ Snapshot created with {len(snapshot['category_usage'])} categories analyzed")
    
    return deleted_count, len(deletion_errors)


def main():
    parser = argparse.ArgumentParser(description='Clean up old empty PocketSmith categories')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Analyze categories but do not delete anything')
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
        print(f"Cleaning up categories for user: {user_info['email']}")
        
        if args.dry_run:
            print("\n🔍 DRY RUN MODE - No categories will be deleted")
        
        # Perform cleanup
        deleted_count, error_count = cleanup_old_categories(client, user_id, dry_run=args.dry_run)
        
        if not args.dry_run:
            print(f"\n✅ Cleanup completed: {deleted_count} categories deleted")
            if error_count > 0:
                print(f"⚠️  {error_count} errors occurred during deletion")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()