import io

def test_csv_import_validation_and_duplicate_detection(client, auth_headers):
    # CSV with valid rows, an invalid row, and a duplicate
    csv_content = (
        "date,raw_description,amount,transaction_type,category\n"
        "2026-09-01,Trader Joes Manhattan,65.40,Expense,Groceries\n"
        "2026-09-02,Uber Trip NYC,32.10,Expense,Transportation\n"
        "2026-09-03,Invalid Date Row,abc,Expense,Food & Dining\n"
    ).encode("utf-8")

    file_obj = io.BytesIO(csv_content)
    res = client.post(
        "/api/v1/transactions/import-csv",
        files={"file": ("test_import.csv", file_obj, "text/csv")},
        headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["imported"] == 2
    assert data["skipped_duplicates"] == 0
    assert len(data["errors"]) == 1
    assert "Invalid amount" in data["errors"][0]

    # Re-upload same CSV to test duplicate detection
    file_obj.seek(0)
    res_dup = client.post(
        "/api/v1/transactions/import-csv",
        files={"file": ("test_import.csv", file_obj, "text/csv")},
        headers=auth_headers
    )
    assert res_dup.status_code == 200
    data_dup = res_dup.json()
    assert data_dup["imported"] == 0
    assert data_dup["skipped_duplicates"] == 2

def test_csv_export(client, auth_headers):
    # Create a transaction
    client.post(
        "/api/v1/transactions",
        json={
            "date": "2026-09-15",
            "raw_description": "WHOLE FOODS MKT",
            "amount": 120.50,
            "transaction_type": "Expense",
            "category": "Groceries"
        },
        headers=auth_headers
    )

    export_res = client.get("/api/v1/transactions/export-csv", headers=auth_headers)
    assert export_res.status_code == 200
    assert export_res.headers["content-type"] == "text/csv; charset=utf-8"
    assert "WHOLE FOODS MKT" in export_res.text
    assert "120.5" in export_res.text
