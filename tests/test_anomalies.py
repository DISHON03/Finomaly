from backend.app.models.transaction import Transaction

def test_anomaly_detection_and_review(db, test_user, client, auth_headers):
    # Add 15 typical coffee transactions of ~$5
    for i in range(1, 16):
        day = f"{i:02d}"
        db.add(Transaction(
            user_id=test_user.id,
            date=f"2026-08-{day}",
            raw_description="Local Coffee Shop",
            clean_merchant="Coffee Shop",
            amount=5.0,
            transaction_type="Expense",
            category="Food & Dining",
            budget_bucket="Wants"
        ))
    
    # Add a major outlier of $380
    outlier = Transaction(
        user_id=test_user.id,
        date="2026-08-20",
        raw_description="Gourmet Espresso Machine",
        clean_merchant="Espresso Lab",
        amount=380.0,
        transaction_type="Expense",
        category="Food & Dining",
        budget_bucket="Wants"
    )
    db.add(outlier)
    db.commit()

    # Trigger scan
    scan_res = client.post("/api/v1/anomalies/scan", headers=auth_headers)
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["new_anomalies_detected"] >= 1
    
    # Find alert for the outlier
    alerts = scan_data["alerts"]
    outlier_alert = next((a for a in alerts if a["difference_amount"] and a["difference_amount"] > 300), None)
    assert outlier_alert is not None
    assert outlier_alert["status"] == "active"
    assert "higher than your median" in outlier_alert["explanation"]

    # Review / dismiss alert
    alert_id = outlier_alert["id"]
    patch_res = client.patch(f"/api/v1/anomalies/{alert_id}/status", json={"status": "dismissed"}, headers=auth_headers)
    assert patch_res.status_code == 200

    # Verify dismissed in list
    list_res = client.get("/api/v1/anomalies?status=dismissed", headers=auth_headers)
    assert list_res.status_code == 200
    assert any(a["id"] == alert_id for a in list_res.json())
