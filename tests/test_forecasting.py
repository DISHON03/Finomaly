from backend.app.models.transaction import Transaction
from backend.app.models.budget import Budget

def test_expense_forecasting(db, test_user, client, auth_headers):
    # Set a budget of $3,000
    db.add(Budget(
        user_id=test_user.id,
        category="General",
        budget_bucket="Wants",
        monthly_target=3000.0
    ))

    # Add 4 months of expenses
    monthly_data = [
        ("2026-05-15", 2800.0),
        ("2026-06-15", 2950.0),
        ("2026-07-15", 3100.0),
        ("2026-08-15", 3250.0),
    ]
    for date_str, amt in monthly_data:
        db.add(Transaction(
            user_id=test_user.id,
            date=date_str,
            raw_description="Monthly Living Expenses",
            clean_merchant="Living Expenses",
            amount=amt,
            transaction_type="Expense",
            category="Living",
            budget_bucket="Needs"
        ))
    db.commit()

    res = client.get("/api/v1/forecasting?horizon=3", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["historical_months_used"] == 4
    assert "Holt's Linear Trend" in data["model_name"]
    assert len(data["forward_projections"]) > 4
    # Check bounds logic
    forecast_points = [p for p in data["forward_projections"] if p["is_forecast"]]
    assert len(forecast_points) == 3
    for p in forecast_points:
        assert p["upper_bound"] >= p["forecast_spend"]
        assert p["lower_bound"] <= p["forecast_spend"]
    assert data["limitations_note"] != ""
