"""
PocketSmith Category Mapping Configuration

This module contains the mapping from old PocketSmith category IDs to new categories
with appropriate labels. This mapping is shared between the recategorization script
and the cleanup script to ensure consistency.

Each mapping entry contains:
- old_category_id: The original PocketSmith category ID
- new_category: The name of the new category to map to
- label: Optional sub-label for more specific categorization
"""

# Category mapping - old category IDs that should be remapped to new categories
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
    7312273: {"new_category": "Bills", "label": "subscription"},  # Subscription TV (child of Bills)
    7312274: {"new_category": "Bills", "label": "utilities"},  # Water (child of Bills)
    7312275: {"new_category": "Bills", "label": "utilities"},  # Rates (child of Bills)
    7312546: {"new_category": "Dining", "label": "restaurants"},  # Coffee (child of Eating out)
    7312547: {"new_category": "Dining", "label": "takeout"},  # Fast food (child of Eating out)
    7312548: {"new_category": "Dining", "label": "restaurants"},  # Restaurants (child of Eating out)
    7312555: {"new_category": "Giving", "label": "church"},  # Church (child of Giving)
    7312556: {"new_category": "Giving", "label": "missions"},  # Missionary (child of Giving)
    7312557: {"new_category": "Groceries", "label": "supermarkets"},  # Supermarket (child of Groceries)
    7312558: {"new_category": "Groceries", "label": "markets"},  # Asian stores (child of Groceries)
    7312559: {"new_category": "Groceries", "label": "markets"},  # Markets (child of Groceries)
    7312562: {"new_category": "Household", "label": "personal-care"},  # Self-care (child of Household)
    7312563: {"new_category": "Household", "label": "production"},  # Furniture (child of Household)
    7312564: {"new_category": "Household", "label": "maintenance"},  # Gardening (child of Household)
    7312565: {"new_category": "Household", "label": "maintenance"},  # Maintenance (child of Household)
    7312566: {"new_category": "Household", "label": "personal-care"},  # Occasions (child of Household)
    7312567: {"new_category": "Household", "label": "production"},  # Tools (child of Household)
    7666458: {"new_category": "Household", "label": "production"},  # Supplies (child of Household)
    7341096: {"new_category": "Income", "label": None},  # Expense Reimbursement (child of Income)
    7312569: {"new_category": "Bills", "label": "medical"},  # Health (child of Insurance)
    7312570: {"new_category": "Bills", "label": "insurance"},  # Home (child of Insurance)
    7312571: {"new_category": "Transport", "label": "insurance"},  # Motor (child of Insurance)
    7312573: {"new_category": "Bills", "label": "medical"},  # Dental (child of Medical)
    7280205: {"new_category": "Household", "label": "cash"},  # Cash spend (child of Household)
    7312574: {"new_category": "Bills", "label": "medical"},  # Health (child of Medical)
    7312575: {"new_category": "Bills", "label": "medical"},  # Medicine (child of Medical)
    7312576: {"new_category": "Bills", "label": "medical"},  # NDIS (child of Medical)
    7312578: {"new_category": "Mortgage", "label": None},  # Interest (child of Mortgage)
    7312579: {"new_category": "Mortgage", "label": "loans"},  # Loan Repayment (child of Mortgage)
    7312581: {"new_category": "Dining", "label": "restaurants"},  # Alcohol (child of Recreation)
    7312582: {"new_category": "Shopping", "label": "hobbies"},  # Books (child of Recreation) 
    7312583: {"new_category": "Shopping", "label": "hobbies"},  # Gadgets (child of Recreation)
    7312584: {"new_category": "Holidays", "label": None},  # Holidays (child of Recreation)
    7312585: {"new_category": "Holidays", "label": "hotels"},  # Hotels (child of Recreation)
    7312586: {"new_category": "Shopping", "label": "health"},  # Sports (child of Recreation)
    7312588: {"new_category": "Transfer", "label": None},  # Loan payments (child of Transfer)
    7312589: {"new_category": "Transfer", "label": None},  # Inter-account (child of Transfer)
    7312591: {"new_category": "Transport", "label": "fines"},  # Fines (child of Transport)
    7312592: {"new_category": "Holidays", "label": "flights"},  # Flights (child of Transport)
    7312593: {"new_category": "Transport", "label": "parking"},  # Parking (child of Transport)
    7312594: {"new_category": "Transport", "label": "petrol"},  # Petrol (child of Transport)
    7312595: {"new_category": "Transport", "label": "public-transport"},  # Public transport (child of Transport)
    7312597: {"new_category": "Transport", "label": "car"},  # Registration (child of Transport)
    7312598: {"new_category": "Transport", "label": "car"},  # Servicing (child of Transport)
    7707848: {"new_category": "Transport", "label": "car"},  # Taxi (child of Transport)
    7312596: {"new_category": "Transport", "label": "tolls"},  # Tolls (child of Transport)
    7280189: {"new_category": "Groceries", "label": "supermarkets"},  # Supermarket (child of Groceries)
    7280190: {"new_category": "Groceries", "label": "markets"},  # Markets (child of Groceries)
    7280191: {"new_category": "Groceries", "label": "markets"},  # Asian stores (child of Groceries)
    7280192: {"new_category": "Dining", "label": "restaurants"},  # Bubble tea (child of Groceries - but should be dining)
    
    # Additional missing categories found in transaction analysis
    7314164: {"new_category": "Shopping", "label": "hobbies"},  # Entertainment -> Shopping
    7312545: {"new_category": "Dining", "label": "restaurants"},  # Bubble tea -> Dining  
    7280182: {"new_category": "Transfer", "label": None},  # Credit Card Payments -> Transfer
    7314704: {"new_category": "Income", "label": "salary"},  # Salary -> Income
    7314705: {"new_category": "Income", "label": "superannuation"},  # Superannuation -> Income
    7312600: {"new_category": "Shopping", "label": "hobbies"},  # Games -> Shopping
    7314702: {"new_category": "Income", "label": "investment"},  # Investment -> Income
    7312550: {"new_category": "Education", "label": "childcare"},  # Childcare -> Education
    7312553: {"new_category": "Education", "label": "classes"},  # Tutoring -> Education
    7314701: {"new_category": "Income", "label": "tax"},  # Tax -> Income
    7280222: {"new_category": "Giving", "label": "gifts"},  # Gifts -> Giving
    7312552: {"new_category": "Education", "label": "classes"},  # School -> Education
}


def get_mapping_for_category(category_id):
    """Get the mapping configuration for a specific category ID"""
    return CATEGORY_MAPPING.get(category_id)


def get_all_old_category_ids():
    """Get all old category IDs that should be cleaned up"""
    return list(CATEGORY_MAPPING.keys())


def get_categories_by_new_name(new_category_name):
    """Get all old category IDs that map to a specific new category name"""
    return [
        category_id for category_id, mapping in CATEGORY_MAPPING.items()
        if mapping["new_category"] == new_category_name
    ]


def get_mapping_summary():
    """Get a summary of the category mapping"""
    new_categories = {}
    for old_id, mapping in CATEGORY_MAPPING.items():
        new_name = mapping["new_category"]
        if new_name not in new_categories:
            new_categories[new_name] = []
        new_categories[new_name].append(old_id)
    
    return {
        "total_old_categories": len(CATEGORY_MAPPING),
        "unique_new_categories": len(new_categories),
        "new_category_breakdown": new_categories
    }