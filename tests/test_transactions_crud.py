def test_create_read_update_delete_transaction(client, auth_headers):
    # 1. Create transaction with auto-categorization fallback
    payload = {
        "date": "2026-09-10",
        "raw_description": "STARBUCKS COFFEE NYC #0281",
        "amount": 8.75,
        "transaction_type": "Expense",
        "category": "Uncategorized",  # Expect auto-suggest to map to Food & Dining
        "payment_channel": "Card"
    }
    create_res = client.post("/api/v1/transactions", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    tx_data = create_res.json()
    assert tx_data["amount"] == 8.75
    assert tx_data["category"] == "Food & Dining"
    assert tx_data["clean_merchant"] == "Starbucks Coffee"
    tx_id = tx_data["id"]

    # 2. Get transaction
    get_res = client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == tx_id

    # 3. Update transaction & verify custom rule is learned
    update_res = client.put(
        f"/api/v1/transactions/{tx_id}",
        json={"category": "Entertainment & Subscriptions", "notes": "Special coffee budget"},
        headers=auth_headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["category"] == "Entertainment & Subscriptions"
    assert update_res.json()["notes"] == "Special coffee budget"

    # Verify rule was stored
    rules_res = client.get("/api/v1/categorization/rules", headers=auth_headers)
    assert rules_res.status_code == 200
    rules = rules_res.json()
    assert any("starbucks" in r["keyword_pattern"] for r in rules)

    # 4. List transactions with search
    list_res = client.get("/api/v1/transactions?search=starbucks", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1

    # 5. Delete transaction
    del_res = client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 6. Verify deleted
    get_after = client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert get_after.status_code == 404
