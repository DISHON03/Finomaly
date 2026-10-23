import io
import re
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime

HEADER_SYNONYMS = {
    "date": ["date", "transaction_date", "trans_date", "posting_date", "timestamp"],
    "raw_description": ["raw_description", "description", "memo", "details", "merchant", "payee", "name"],
    "amount": ["amount", "cost", "total", "value", "price", "net_amount"],
    "transaction_type": ["transaction_type", "type", "tx_type", "debit_credit"],
    "category": ["category", "cat", "expense_category"],
    "subcategory": ["subcategory", "sub_category", "sub_cat"],
    "account_id": ["account_id", "account", "acct"],
}

def normalize_column_name(col: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "", col.lower().strip().replace(" ", "_"))
    for standard_col, synonyms in HEADER_SYNONYMS.items():
        if cleaned in synonyms:
            return standard_col
    return cleaned

def parse_date(date_val: Any) -> Optional[str]:
    if pd.isna(date_val) or not str(date_val).strip():
        return None
    s = str(date_val).strip()
    # Try parsing common formats
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%m-%d-%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    try:
        dt = pd.to_datetime(s)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None

def parse_amount(amount_val: Any) -> Tuple[Optional[float], Optional[str]]:
    """
    Parses amount string or number.
    Returns (cleaned_positive_amount, inferred_type).
    """
    if pd.isna(amount_val):
        return None, None
    s = str(amount_val).strip()
    s = s.replace("$", "").replace("₹", "").replace("€", "").replace("£", "").replace(",", "")
    
    try:
        val = float(s)
    except ValueError:
        return None, None

    if val < 0:
        return abs(round(val, 2)), "Expense"
    return round(val, 2), None

def clean_merchant_string(raw: str) -> str:
    """Derives clean merchant name by removing POS noise, card asterisks, city suffixes."""
    cleaned = raw.strip()
    # Remove terminal/store IDs like #1234, *1234
    cleaned = re.sub(r"[\*#]\w+", "", cleaned)
    # Remove generic location words like NYC, NY, POS, E-PAY, ACH, DIRECT DEP
    cleaned = re.sub(r"\b(NYC|NY|STORE|PAYGO|ACH|E-PAY|ONLINE|WEB|APP|POS)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.title() if cleaned else raw.strip().title()

def parse_and_validate_csv(file_bytes: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Parses CSV bytes, maps columns, validates rows, and returns clean dict list and validation errors.
    """
    errors = []
    parsed_rows = []

    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        return [], [f"Failed to read CSV file: {str(e)}"]

    if df.empty:
        return [], ["The provided CSV file contains no records."]

    # Rename columns using synonyms
    col_map = {orig: normalize_column_name(orig) for orig in df.columns}
    df = df.rename(columns=col_map)

    # Validate required columns
    required = ["date", "raw_description", "amount"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        return [], [f"Missing mandatory column(s): {', '.join(missing)}. Detected columns: {list(df.columns)}"]

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed header + 1
        raw_date = row.get("date")
        parsed_d = parse_date(raw_date)
        if not parsed_d:
            errors.append(f"Row {row_num}: Invalid date '{raw_date}'")
            continue

        raw_desc = str(row.get("raw_description", "")).strip()
        if not raw_desc or raw_desc.lower() == "nan":
            errors.append(f"Row {row_num}: Missing description")
            continue

        amount_val, inferred_type = parse_amount(row.get("amount"))
        if amount_val is None or amount_val == 0:
            errors.append(f"Row {row_num}: Invalid amount '{row.get('amount')}'")
            continue

        # Inferred or explicit type
        tx_type = row.get("transaction_type")
        if pd.isna(tx_type) or str(tx_type).strip() == "":
            tx_type = inferred_type or "Expense"
        else:
            tx_type = str(tx_type).strip().title()
            if tx_type not in ["Expense", "Income", "Transfer"]:
                tx_type = "Expense"

        category = row.get("category")
        if pd.isna(category) or str(category).strip() == "":
            category = "Uncategorized"
        else:
            category = str(category).strip().title()

        clean_merchant = row.get("clean_merchant")
        if pd.isna(clean_merchant) or not str(clean_merchant).strip():
            clean_merchant = clean_merchant_string(raw_desc)
        else:
            clean_merchant = str(clean_merchant).strip().title()

        budget_bucket = row.get("budget_bucket")
        if pd.isna(budget_bucket) or str(budget_bucket).strip() == "":
            budget_bucket = "Income" if tx_type == "Income" else "Wants"
        else:
            budget_bucket = str(budget_bucket).strip().title()

        parsed_rows.append({
            "date": parsed_d,
            "raw_description": raw_desc,
            "clean_merchant": clean_merchant,
            "amount": amount_val,
            "transaction_type": tx_type,
            "category": category,
            "subcategory": str(row.get("subcategory", "")).strip() if not pd.isna(row.get("subcategory")) else "",
            "budget_bucket": budget_bucket,
            "is_recurring": bool(row.get("is_recurring", False)) if not pd.isna(row.get("is_recurring")) else False,
            "payment_channel": str(row.get("payment_channel", "Card")).strip() if not pd.isna(row.get("payment_channel")) else "Card",
            "city": str(row.get("city", "Online")).strip() if not pd.isna(row.get("city")) else "Online",
            "state": str(row.get("state", "US")).strip() if not pd.isna(row.get("state")) else "US",
            "account_id": str(row.get("account_id", "")).strip() if not pd.isna(row.get("account_id")) else None,
        })

    return parsed_rows, errors
