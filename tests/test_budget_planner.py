def test_budget_planner_and_utilization(client, auth_headers):
    # Set a budget for Groceries of $400 with threshold 80%
    b_res = client.post(
        "/api/v1/budgets",
        json={
            "category": "Groceries",
            "budget_bucket": "Needs",
            "monthly_target": 400.0,
            "alert_threshold": 80.0
        },
        headers=auth_headers
    )
    assert b_res.status_code == 201
    b_id = b_res.json()["id"]

    # Add transaction of $350 in Groceries (87.5% utilization -> APPROACHING)
    client.post(
        "/api/v1/transactions",
        json={
            "date": "2026-09-05",
            "raw_description": "Costco Wholesale Bulk",
            "amount": 350.0,
            "transaction_type": "Expense",
            "category": "Groceries",
            "budget_bucket": "Needs"
        },
        headers=auth_headers
    )

    summary_res = client.get("/api/v1/budgets/summary", headers=auth_headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_budget"] == 400.0
    assert summary["total_spent"] == 350.0
    assert summary["remaining_total"] == 50.0
    assert summary["overall_utilization_pct"] == 87.5

    # Check category item status
    item = summary["items"][0]
    assert item["category"] == "Groceries"
    assert item["status"] == "APPROACHING"

    # Add another transaction of $100 -> total $450 (112.5% -> EXCEEDED)
    client.post(
        "/api/v1/transactions",
        json={
            "date": "2026-09-12",
            "raw_description": "Trader Joe's extras",
            "amount": 100.0,
            "transaction_type": "Expense",
            "category": "Groceries",
            "budget_bucket": "Needs"
        },
        headers=auth_headers
    )

    summary_res2 = client.get("/api/v1/budgets/summary", headers=auth_headers)
    assert summary_res2.status_code == 200
    item2 = summary_res2.json()["items"][0]
    assert item2["actual_spent"] == 450.0
    assert item2["status"] == "EXCEEDED"
    assert item2["remaining_amount"] == -50.0
