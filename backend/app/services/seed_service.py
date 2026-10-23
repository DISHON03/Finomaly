import os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.budget import Budget
from backend.app.models.transaction import Transaction
from backend.app.models.savings_goal import SavingsGoal, GoalContribution
from backend.app.models.anomaly import AnomalyAlert
from backend.app.models.user_preference import UserPreference
from backend.app.utils.security import hash_password
from backend.app.services.anomaly_service import run_spending_anomaly_scan
from backend.app.services.tableau_service import export_all_tableau_files

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RAW_TRANSACTIONS_CSV = os.path.join(BASE_DIR, "data", "raw", "raw_transactions.csv")
ACCOUNTS_CSV = os.path.join(BASE_DIR, "data", "raw", "accounts.csv")
BUDGETS_CSV = os.path.join(BASE_DIR, "data", "raw", "monthly_budgets.csv")

DEMO_EMAIL = "demo@finomaly.io"
DEMO_PASSWORD = "finomaly123"

DEFAULT_BUDGETS = [
    ("Housing", "Needs", 2400.0, 80.0),
    ("Utilities", "Needs", 350.0, 85.0),
    ("Groceries", "Needs", 650.0, 80.0),
    ("Food & Dining", "Wants", 550.0, 75.0),
    ("Transportation", "Needs", 300.0, 80.0),
    ("Entertainment & Subscriptions", "Wants", 280.0, 80.0),
    ("Shopping", "Wants", 400.0, 75.0),
    ("Health & Medical", "Needs", 200.0, 85.0),
    ("Savings & Investments", "Savings", 1200.0, 90.0),
]

def seed_demo_data_if_needed(db: Session) -> User:
    """Creates demo user and populates realistic multi-year transaction data if not present."""
    demo_user = db.query(User).filter(
        (User.email == DEMO_EMAIL) | (User.email == "demo@spendsense.io") | (User.is_demo == True)
    ).first()
    if demo_user:
        # Seamlessly update legacy demo email to Finomaly
        if demo_user.email == "demo@spendsense.io":
            demo_user.email = DEMO_EMAIL
            demo_user.hashed_password = hash_password(DEMO_PASSWORD)
            db.commit()
            db.refresh(demo_user)
        # Check if transactions already exist
        tx_count = db.query(Transaction).filter(Transaction.user_id == demo_user.id).count()
        if tx_count > 0:
            return demo_user

    if not demo_user:
        demo_user = User(
            email=DEMO_EMAIL,
            hashed_password=hash_password(DEMO_PASSWORD),
            full_name="Alex Morgan (Demo Account)",
            is_demo=True
        )
        db.add(demo_user)
        db.flush()

        pref = UserPreference(
            user_id=demo_user.id,
            theme="dark",
            currency_symbol="$",
            monthly_savings_target_pct=20.0,
            anomaly_sensitivity="balanced"
        )
        db.add(pref)
        db.commit()
        db.refresh(demo_user)

    # Seed Accounts
    accounts_data = [
        ("ACC_CHK_01", "Chase Total Checking", "Checking", 5420.50),
        ("ACC_SAV_01", "Ally High-Yield Savings", "Savings", 18500.00),
        ("ACC_CC_01", "Chase Sapphire Preferred", "Credit Card", -1240.20),
        ("ACC_CC_02", "Amex Blue Cash Everyday", "Credit Card", -680.45),
    ]
    for acc_id, name, acc_type, bal in accounts_data:
        existing = db.query(Account).filter(Account.account_id == acc_id).first()
        if not existing:
            db.add(Account(account_id=acc_id, user_id=demo_user.id, name=name, type=acc_type, balance=bal))
    db.commit()

    # Seed Budgets
    for cat, bucket, target, alert_th in DEFAULT_BUDGETS:
        existing = db.query(Budget).filter(Budget.user_id == demo_user.id, Budget.category == cat).first()
        if not existing:
            db.add(Budget(
                user_id=demo_user.id,
                category=cat,
                budget_bucket=bucket,
                monthly_target=target,
                alert_threshold=alert_th
            ))
    db.commit()

    # Seed Savings Goals
    goals_data = [
        ("Emergency Safety Net", 15000.0, 9500.0, "2026-12-31", "Emergency", "6 months of essential living expenses"),
        ("Tokyo & Kyoto Vacation", 5000.0, 3200.0, "2027-04-15", "Travel", "Cherry blossom season flight & hotel fund"),
        ("Tesla Model Y Downpayment", 10000.0, 4800.0, "2027-09-01", "Vehicle", "Target 20% downpayment"),
    ]
    for g_name, target, curr, target_d, cat, notes in goals_data:
        g = db.query(SavingsGoal).filter(SavingsGoal.user_id == demo_user.id, SavingsGoal.name == g_name).first()
        if not g:
            new_g = SavingsGoal(
                user_id=demo_user.id,
                name=g_name,
                target_amount=target,
                current_amount=curr,
                target_date=target_d,
                category=cat,
                notes=notes,
                is_completed=False
            )
            db.add(new_g)
            db.flush()

            # Add contributions
            db.add(GoalContribution(
                goal_id=new_g.id,
                user_id=demo_user.id,
                amount=round(curr * 0.4, 2),
                date="2026-07-15",
                notes="Initial lump-sum contribution"
            ))
            db.add(GoalContribution(
                goal_id=new_g.id,
                user_id=demo_user.id,
                amount=round(curr * 0.3, 2),
                date="2026-08-15",
                notes="Monthly allocation"
            ))
            db.add(GoalContribution(
                goal_id=new_g.id,
                user_id=demo_user.id,
                amount=round(curr * 0.3, 2),
                date="2026-09-15",
                notes="Monthly allocation"
            ))
    db.commit()

    # Load Transactions
    if os.path.exists(RAW_TRANSACTIONS_CSV):
        print(f"Loading demo transactions from {RAW_TRANSACTIONS_CSV}...")
        df = pd.read_csv(RAW_TRANSACTIONS_CSV)
        # Limit or load all transactions (e.g. 1500 records for fast responsiveness)
        df_sample = df.tail(1200)

        tx_objects = []
        for _, row in df_sample.iterrows():
            tx_objects.append(Transaction(
                transaction_id=str(row.get("transaction_id", "")),
                user_id=demo_user.id,
                account_id=str(row.get("account_id", "ACC_CHK_01")),
                date=str(row.get("date", "2026-01-01")),
                raw_description=str(row.get("raw_description", "")),
                clean_merchant=str(row.get("clean_merchant", "Merchant")),
                amount=round(float(row.get("amount", 0.0)), 2),
                transaction_type=str(row.get("transaction_type", "Expense")),
                category=str(row.get("category", "General")),
                subcategory=str(row.get("subcategory", "")),
                budget_bucket=str(row.get("budget_bucket", "Wants")),
                is_recurring=bool(row.get("is_recurring", False)),
                payment_channel=str(row.get("payment_channel", "Card")),
                city=str(row.get("city", "New York")),
                state=str(row.get("state", "NY")),
                is_demo=True
            ))
        db.bulk_save_objects(tx_objects)
        db.commit()
        print(f"Successfully seeded {len(tx_objects)} transactions for demo user.")

    # Run anomaly detection scan and export initial Tableau datasets
    try:
        run_spending_anomaly_scan(db, demo_user.id)
        export_all_tableau_files(db, demo_user.id)
    except Exception as e:
        print(f"Initial anomaly scan warning: {e}")

    return demo_user

def reset_demo_data(db: Session, user_id: int):
    """Purges user data and re-seeds fresh baseline."""
    db.query(Transaction).filter(Transaction.user_id == user_id).delete()
    db.query(Budget).filter(Budget.user_id == user_id).delete()
    db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).delete()
    db.query(GoalContribution).filter(GoalContribution.user_id == user_id).delete()
    db.query(AnomalyAlert).filter(AnomalyAlert.user_id == user_id).delete()
    db.commit()
    seed_demo_data_if_needed(db)
