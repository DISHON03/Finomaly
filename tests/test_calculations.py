import pytest
from backend.app.models.transaction import Transaction

def test_income_and_expense_calculations(db, test_user, client, auth_headers):
    # Add income
    db.add(Transaction(
        user_id=test_user.id,
        date="2026-09-01",
        raw_description="Payroll Direct Deposit",
        clean_merchant="TechNova Corp",
        amount=5000.0,
        transaction_type="Income",
        category="Income",
        subcategory="Salary",
        budget_bucket="Income"
    ))
    # Add expenses
    db.add(Transaction(
        user_id=test_user.id,
        date="2026-09-02",
        raw_description="Rent Payment",
        clean_merchant="Apartment Community",
        amount=2000.0,
        transaction_type="Expense",
        category="Housing",
        subcategory="Rent",
        budget_bucket="Needs"
    ))
    db.add(Transaction(
        user_id=test_user.id,
        date="2026-09-03",
        raw_description="Grocery Supermarket",
        clean_merchant="Trader Joe's",
        amount=500.0,
        transaction_type="Expense",
        category="Groceries",
        subcategory="Supermarkets",
        budget_bucket="Needs"
    ))
    db.add(Transaction(
        user_id=test_user.id,
        date="2026-09-04",
        raw_description="Dinner with friends",
        clean_merchant="Italian Restaurant",
        amount=500.0,
        transaction_type="Expense",
        category="Food & Dining",
        subcategory="Restaurants",
        budget_bucket="Wants"
    ))
    db.commit()

    # Query KPI endpoint
    res = client.get("/api/v1/dashboard/kpis", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    assert data["total_income"] == 5000.0
    assert data["total_expenses"] == 3000.0
    assert data["remaining_balance"] == 2000.0
    # Savings rate = (5000 - 3000) / 5000 * 100 = 40.0%
    assert data["savings_rate"] == 40.0

    # Needs spend: 2000 + 500 = 2500 (50.0%)
    assert data["needs_spend"] == 2500.0
    assert data["needs_pct"] == 50.0

    # Wants spend: 500 (10.0%)
    assert data["wants_spend"] == 500.0
    assert data["wants_pct"] == 10.0
