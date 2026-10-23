def test_user_data_isolation(client, auth_headers, auth_headers2):
    # User 1 creates a private transaction
    res1 = client.post(
        "/api/v1/transactions",
        json={
            "date": "2026-09-01",
            "raw_description": "User 1 Secret Transaction",
            "amount": 999.0,
            "transaction_type": "Expense",
            "category": "Shopping"
        },
        headers=auth_headers
    )
    assert res1.status_code == 201
    tx_id = res1.json()["id"]

    # User 2 lists transactions -> MUST NOT see User 1's transaction
    res2_list = client.get("/api/v1/transactions", headers=auth_headers2)
    assert res2_list.status_code == 200
    txs_user2 = res2_list.json()["transactions"]
    assert not any(t["id"] == tx_id for t in txs_user2)

    # User 2 attempts to directly GET User 1's transaction -> MUST return 404
    res2_get = client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers2)
    assert res2_get.status_code == 404

    # User 2 attempts to DELETE User 1's transaction -> MUST return 404
    res2_del = client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers2)
    assert res2_del.status_code == 404

def test_api_error_handling(client, auth_headers):
    # Missing auth headers returns 401
    res_no_auth = client.post("/api/v1/transactions", json={"amount": 100.0})
    assert res_no_auth.status_code == 401

    # Missing required fields in transaction creation with auth returns 422
    res_bad = client.post("/api/v1/transactions", json={"amount": -50.0}, headers=auth_headers)
    assert res_bad.status_code in (400, 422)

    # Invalid login credentials
    res_login_bad = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@finomaly.io", "password": "wrongpassword"}
    )
    assert res_login_bad.status_code == 401

    # Register duplicate email
    client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@finomaly.io", "password": "password123", "full_name": "First User"}
    )
    res_dup = client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@finomaly.io", "password": "password123", "full_name": "Second User"}
    )
    assert res_dup.status_code == 400
    assert "already exists" in res_dup.json()["detail"]
