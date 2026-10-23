import io
import pandas as pd
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionOut,
    TransactionListResponse, CSVImportResult
)
from backend.app.services.auth_service import get_current_user
from backend.app.services.categorization_service import suggest_category_for_description, record_user_correction
from backend.app.utils.csv_parser import parse_and_validate_csv, clean_merchant_string

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    search: Optional[str] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    budget_bucket: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if search:
        search_term = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                Transaction.raw_description.ilike(search_term),
                Transaction.clean_merchant.ilike(search_term),
                Transaction.category.ilike(search_term),
                Transaction.subcategory.ilike(search_term)
            )
        )

    if category and category != "All":
        query = query.filter(Transaction.category == category)

    if transaction_type and transaction_type != "All":
        query = query.filter(Transaction.transaction_type == transaction_type)

    if budget_bucket and budget_bucket != "All":
        query = query.filter(Transaction.budget_bucket == budget_bucket)

    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    total = query.count()
    txs = query.order_by(desc(Transaction.date), desc(Transaction.id)).offset((page - 1) * page_size).limit(page_size).all()

    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        transactions=[TransactionOut.model_validate(t) for t in txs]
    )

@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_in: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    merchant = tx_in.clean_merchant or clean_merchant_string(tx_in.raw_description)
    category = tx_in.category
    subcategory = tx_in.subcategory or ""
    budget_bucket = tx_in.budget_bucket or "Wants"

    # Auto-categorize if user didn't specify or left as Uncategorized
    if not category or category.lower() in ("uncategorized", "general", "other"):
        suggestion = suggest_category_for_description(db, current_user.id, tx_in.raw_description)
        category = suggestion.suggested_category
        subcategory = suggestion.suggested_subcategory
        budget_bucket = suggestion.suggested_budget_bucket

    tx = Transaction(
        user_id=current_user.id,
        date=tx_in.date,
        raw_description=tx_in.raw_description,
        clean_merchant=merchant,
        amount=tx_in.amount,
        transaction_type=tx_in.transaction_type,
        category=category,
        subcategory=subcategory,
        budget_bucket=budget_bucket,
        is_recurring=tx_in.is_recurring or False,
        payment_channel=tx_in.payment_channel or "Card",
        city=tx_in.city or "Online",
        state=tx_in.state or "US",
        notes=tx_in.notes,
        account_id=tx_in.account_id,
        is_demo=current_user.is_demo
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return TransactionOut.model_validate(tx)

@router.get("/export-csv")
def export_transactions_csv(
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    if category and category != "All":
        query = query.filter(Transaction.category == category)
    if transaction_type and transaction_type != "All":
        query = query.filter(Transaction.transaction_type == transaction_type)
    if date_from:
        query = query.filter(Transaction.date >= date_from)
    if date_to:
        query = query.filter(Transaction.date <= date_to)

    txs = query.order_by(desc(Transaction.date)).all()
    rows = []
    for t in txs:
        rows.append({
            "transaction_id": t.transaction_id or f"TX_{t.id}",
            "date": t.date,
            "merchant": t.clean_merchant,
            "description": t.raw_description,
            "amount": t.amount,
            "type": t.transaction_type,
            "category": t.category,
            "subcategory": t.subcategory,
            "budget_bucket": t.budget_bucket,
            "is_recurring": t.is_recurring,
            "payment_channel": t.payment_channel,
            "city": t.city,
            "state": t.state,
        })

    df = pd.DataFrame(rows)
    csv_str = df.to_csv(index=False)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=finomaly_transactions.csv"}
    )

@router.get("/{id}", response_model=TransactionOut)
def get_transaction(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(Transaction.id == id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return TransactionOut.model_validate(tx)

@router.put("/{id}", response_model=TransactionOut)
def update_transaction(
    id: int,
    tx_in: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(Transaction.id == id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    old_category = tx.category
    update_data = tx_in.model_dump(exclude_unset=True)

    for field, val in update_data.items():
        setattr(tx, field, val)

    # If the user updated the category, save a custom category rule so Finomaly remembers it
    if "category" in update_data and update_data["category"] != old_category:
        record_user_correction(
            db=db,
            user_id=current_user.id,
            raw_description=tx.raw_description,
            category=tx.category,
            subcategory=tx.subcategory or "",
            budget_bucket=tx.budget_bucket or "Wants"
        )

    db.commit()
    db.refresh(tx)
    return TransactionOut.model_validate(tx)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = db.query(Transaction).filter(Transaction.id == id, Transaction.user_id == current_user.id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    db.delete(tx)
    db.commit()
    return None

@router.post("/import-csv", response_model=CSVImportResult)
async def import_transactions_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="CSV file exceeds 10MB maximum limit.")

    parsed_rows, errors = parse_and_validate_csv(content)
    if not parsed_rows and errors:
        return CSVImportResult(total_rows=0, imported=0, skipped_duplicates=0, errors=errors)

    # Fetch existing transaction signatures for duplicate detection
    existing_txs = (
        db.query(Transaction.date, Transaction.amount, Transaction.clean_merchant)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )
    existing_sig_set = {(str(d), float(amt), str(m).lower()) for d, amt, m in existing_txs}

    to_insert = []
    skipped_duplicates = 0

    for row in parsed_rows:
        sig = (str(row["date"]), float(row["amount"]), str(row["clean_merchant"]).lower())
        if sig in existing_sig_set:
            skipped_duplicates += 1
            continue

        # Check smart category suggestion if Uncategorized
        if row["category"] in ("Uncategorized", "General", "Other"):
            sug = suggest_category_for_description(db, current_user.id, row["raw_description"])
            row["category"] = sug.suggested_category
            row["subcategory"] = sug.suggested_subcategory
            row["budget_bucket"] = sug.suggested_budget_bucket

        tx_obj = Transaction(
            user_id=current_user.id,
            date=row["date"],
            raw_description=row["raw_description"],
            clean_merchant=row["clean_merchant"],
            amount=row["amount"],
            transaction_type=row["transaction_type"],
            category=row["category"],
            subcategory=row.get("subcategory", ""),
            budget_bucket=row["budget_bucket"],
            is_recurring=row.get("is_recurring", False),
            payment_channel=row.get("payment_channel", "Card"),
            city=row.get("city", "Online"),
            state=row.get("state", "US"),
            account_id=row.get("account_id"),
            is_demo=False
        )
        to_insert.append(tx_obj)
        existing_sig_set.add(sig)

    if to_insert:
        db.bulk_save_objects(to_insert)
        db.commit()

    return CSVImportResult(
        total_rows=len(parsed_rows),
        imported=len(to_insert),
        skipped_duplicates=skipped_duplicates,
        errors=errors[:15]  # Limit error sample
    )


