import re
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from backend.app.models.category_rule import CategoryRule
from backend.app.schemas.analytics import CategorizationSuggestion

# Built-in Default Keyword Taxonomy
DEFAULT_TAXONOMY_RULES = [
    # Salary & Income
    (r"\b(payroll|salary|dir dep|direct dep|technova|dividend|interest payment|stipend)\b", "Income", "Salary & Wages", "Income"),
    
    # Housing & Utilities
    (r"\b(rent|mortgage|avalon|lease|landlord|apartments|property mgmt)\b", "Housing", "Rent/Mortgage", "Needs"),
    (r"\b(coned|con edison|electric|national grid|gas ny|water board|sewer|pge|duke energy)\b", "Utilities", "Electricity & Gas", "Needs"),
    (r"\b(verizon|fios|comcast|xfinity|spectrum|at&t internet|t-mobile home)\b", "Utilities", "Internet & Mobile", "Needs"),
    
    # Food & Groceries
    (r"\b(trader joe|whole foods|wfm|costco|safeway|kroger|aldi|grocery|supermarket|wegmans|publix|market)\b", "Groceries", "Supermarkets", "Needs"),
    (r"\b(starbucks|blue bottle|dunkin|peet's|coffee|cafe|espresso|roasters)\b", "Food & Dining", "Coffee Shops", "Wants"),
    (r"\b(chipotle|sweetgreen|sushi|trattoria|diner|burger|shake shack|pizza|taco|bistro|steakhouse|restaurant)\b", "Food & Dining", "Restaurants", "Wants"),
    (r"\b(doordash|uber eats|grubhub|postmates|seamless|caviar)\b", "Food & Dining", "Food Delivery", "Wants"),
    
    # Transportation
    (r"\b(shell|chevron|bp|exxon|mobil|gas station|fuel|speedway|sunoco|wawa gas)\b", "Transportation", "Fuel & Gas", "Needs"),
    (r"\b(mta|omny|subway|transit|metro|caltrain|bart|amtrak|bus)\b", "Transportation", "Public Transit", "Needs"),
    (r"\b(uber|lyft|rideshare|taxi|cab)\b", "Transportation", "Rideshare", "Wants"),
    (r"\b(parking|ezpass|toll|spothero|parkmobile)\b", "Transportation", "Parking & Tolls", "Needs"),
    
    # Subscriptions & Entertainment
    (r"\b(netflix|spotify|hulu|disney\+|hbo|max|apple tv|youtube premium|paramount|audible)\b", "Entertainment & Subscriptions", "Streaming Services", "Wants"),
    (r"\b(equinox|planet fitness|gym|fitness|crossfit|orange theory|classpass)\b", "Entertainment & Subscriptions", "Fitness & Wellness", "Wants"),
    (r"\b(cinema|amc|regal|ticketmaster|concert|broadway|eventbrite)\b", "Entertainment & Subscriptions", "Live Events & Movies", "Wants"),
    
    # Shopping
    (r"\b(amazon|amzn|ebay|target|walmart|best buy|apple store|ikea|home depot|lowe's)\b", "Shopping", "General Retail", "Wants"),
    (r"\b(zara|h&m|nordstrom|nike|adidas|uniqlo|sephora|ulta|lululemon|gap)\b", "Shopping", "Apparel & Beauty", "Wants"),
    
    # Healthcare
    (r"\b(cvs|walgreens|duane reade|pharmacy|rx|health|dental|hospital|doctor|urgent care|quest diag)\b", "Health & Medical", "Pharmacy & Care", "Needs"),
    
    # Savings & Transfers
    (r"\b(transfer to|ally hysa|vanguard|fidelity|schwab|robinhood|savings alloc)\b", "Savings & Investments", "Transfers & HYSA", "Savings"),
]

def suggest_category_for_description(db: Session, user_id: int, description: str) -> CategorizationSuggestion:
    """
    Predicts the category, subcategory, and budget bucket for a transaction description.
    First checks user-specific customized correction rules, then built-in taxonomy regex patterns.
    """
    clean_desc = description.strip().lower()

    # 1. Check custom user rules in database
    user_rules = (
        db.query(CategoryRule)
        .filter(CategoryRule.user_id == user_id)
        .order_by(CategoryRule.priority.desc(), CategoryRule.created_at.desc())
        .all()
    )

    for rule in user_rules:
        pattern = rule.keyword_pattern.lower()
        if pattern in clean_desc or re.search(r"\b" + re.escape(pattern) + r"\b", clean_desc):
            return CategorizationSuggestion(
                suggested_category=rule.category,
                suggested_subcategory=rule.subcategory or "",
                suggested_budget_bucket=rule.budget_bucket or "Wants",
                confidence=0.98,
                matched_rule=f"User Learned Rule: '{rule.keyword_pattern}'"
            )

    # 2. Check built-in taxonomy rules
    for regex_pat, cat, subcat, bucket in DEFAULT_TAXONOMY_RULES:
        if re.search(regex_pat, clean_desc, flags=re.IGNORECASE):
            return CategorizationSuggestion(
                suggested_category=cat,
                suggested_subcategory=subcat,
                suggested_budget_bucket=bucket,
                confidence=0.90,
                matched_rule=f"Pattern: {regex_pat}"
            )

    # 3. Fallback
    return CategorizationSuggestion(
        suggested_category="Other & Miscellaneous",
        suggested_subcategory="General",
        suggested_budget_bucket="Wants",
        confidence=0.40,
        matched_rule=None
    )

def record_user_correction(
    db: Session, 
    user_id: int, 
    raw_description: str, 
    category: str, 
    subcategory: str = "", 
    budget_bucket: str = "Wants"
) -> CategoryRule:
    """
    Remembers user corrections by creating or updating a CategoryRule.
    Extracts the most salient keyword or phrase from raw_description.
    """
    # Extract clean keyword: take first 2 words or clean string
    tokens = re.sub(r"[^a-zA-Z0-9\s]", " ", raw_description.lower()).split()
    keyword = " ".join(tokens[:2]) if len(tokens) >= 2 else (tokens[0] if tokens else raw_description.lower())

    existing_rule = (
        db.query(CategoryRule)
        .filter(CategoryRule.user_id == user_id, CategoryRule.keyword_pattern == keyword)
        .first()
    )

    if existing_rule:
        existing_rule.category = category
        existing_rule.subcategory = subcategory
        existing_rule.budget_bucket = budget_bucket
        existing_rule.priority += 1
        db.commit()
        db.refresh(existing_rule)
        return existing_rule
    else:
        new_rule = CategoryRule(
            user_id=user_id,
            keyword_pattern=keyword,
            category=category,
            subcategory=subcategory,
            budget_bucket=budget_bucket,
            priority=1
        )
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        return new_rule
