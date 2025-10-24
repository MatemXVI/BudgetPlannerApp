from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def register_and_login(client: TestClient, email: str = "user1@example.com", password: str = "S3cretPass!"):
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    r = client.post("/api/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_categories_crud_and_detach_on_delete(client: TestClient):
    token = register_and_login(client)

    # Create category
    r = client.post("/api/categories", json={"name": "Jedzenie"}, headers=auth_header(token))
    assert r.status_code == 201, r.text
    cat = r.json()

    # Create transaction in this category
    now = datetime.now(timezone.utc)
    tx_payload = {
        "category_id": cat["id"],
        "type": "expense",
        "amount": "25.50",
        "description": "Zakupy",
        "date": now.isoformat(),
        "is_planned": False,
    }
    r = client.post("/api/transactions", json=tx_payload, headers=auth_header(token))
    assert r.status_code == 201, r.text
    tx = r.json()

    # Delete category (should detach, not delete transaction)
    r = client.delete(f"/api/categories/{cat['id']}", headers=auth_header(token))
    assert r.status_code in (200, 204)

    # Transaction should still exist with category_id = null
    r = client.get(f"/api/transactions/{tx['id']}", headers=auth_header(token))
    assert r.status_code == 200
    got = r.json()
    assert got["id"] == tx["id"]
    assert got["category_id"] is None

    # Categories list should be empty
    r = client.get("/api/categories", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json() == []


def test_transactions_filters_and_reports(client: TestClient):
    token = register_and_login(client, email="reporter@example.com")

    # Create categories
    r = client.post("/api/categories", json={"name": "Pensja"}, headers=auth_header(token))
    assert r.status_code == 201
    cat_income = r.json()
    r = client.post("/api/categories", json={"name": "Transport"}, headers=auth_header(token))
    assert r.status_code == 201
    cat_expense = r.json()

    now = datetime.now(timezone.utc)
    last_month = (now.replace(day=1) - timedelta(days=1)).replace(day=1)

    # Add income (this month)
    r = client.post(
        "/api/transactions",
        json={
            "category_id": cat_income["id"],
            "type": "income",
            "amount": "3000.00",
            "description": "Wypłata",
            "date": now.isoformat(),
            "is_planned": False,
        },
        headers=auth_header(token),
    )
    assert r.status_code == 201

    # Add expense (this month)
    r = client.post(
        "/api/transactions",
        json={
            "category_id": cat_expense["id"],
            "type": "expense",
            "amount": "120.55",
            "description": "Bilet",
            "date": now.isoformat(),
            "is_planned": False,
        },
        headers=auth_header(token),
    )
    assert r.status_code == 201

    # Add expense last month (should not affect current monthly report)
    r = client.post(
        "/api/transactions",
        json={
            "category_id": cat_expense["id"],
            "type": "expense",
            "amount": "200.00",
            "description": "Taxi",
            "date": last_month.isoformat(),
            "is_planned": False,
        },
        headers=auth_header(token),
    )
    assert r.status_code == 201

    # List filter: income only
    r = client.get("/api/transactions?type=income", headers=auth_header(token))
    assert r.status_code == 200
    income_items = r.json()
    assert all(i["type"] == "income" for i in income_items)

    # Balance report should include both current-month income and expense totals (all-time sums)
    r = client.get("/api/reports/balance", headers=auth_header(token))
    assert r.status_code == 200
    bal = r.json()
    assert bal["income"] == "3000.00"
    # total expense is 120.55 + 200.00 = 320.55
    assert bal["expense"] == "320.55"
    assert bal["net"] == "2679.45"

    # Monthly report (defaults to current month) should exclude last month's 200.00
    r = client.get("/api/reports/monthly", headers=auth_header(token))
    assert r.status_code == 200
    monthly = r.json()
    assert monthly["income"] == "3000.00"
    assert monthly["expense"] == "120.55"
    assert monthly["net"] == "2879.45"

    # By category: both categories should appear with appropriate sums
    r = client.get("/api/reports/by-category", headers=auth_header(token))
    assert r.status_code == 200
    rows = r.json()
    names = {row["category_name"]: row for row in rows}
    assert names["Pensja"]["income"] == "3000.00"
    # Transport expenses total 320.55 (both months)
    assert names["Transport"]["expense"] == "320.55"


def test_debug_clear_removes_user_data_only(client: TestClient):
    # Two users with separate data
    t1 = register_and_login(client, email="u1@example.com")
    t2 = register_and_login(client, email="u2@example.com")

    # User 1 creates a category and tx
    r = client.post("/api/categories", json={"name": "C1"}, headers=auth_header(t1))
    assert r.status_code == 201
    cat1 = r.json()
    r = client.post(
        "/api/transactions",
        json={
            "category_id": cat1["id"],
            "type": "expense",
            "amount": "10.00",
            "description": "x",
            "date": datetime.now(timezone.utc).isoformat(),
            "is_planned": False,
        },
        headers=auth_header(t1),
    )
    assert r.status_code == 201

    # User 2 creates their own data
    r = client.post("/api/categories", json={"name": "C2"}, headers=auth_header(t2))
    assert r.status_code == 201

    # Clear user1 data
    r = client.post("/api/debug/clear", headers=auth_header(t1))
    assert r.status_code == 200
    payload = r.json()
    assert payload["categories_deleted"] >= 1

    # User1 should see no categories
    r = client.get("/api/categories", headers=auth_header(t1))
    assert r.status_code == 200
    assert r.json() == []

    # User2 data unaffected
    r = client.get("/api/categories", headers=auth_header(t2))
    assert r.status_code == 200
    cats2 = r.json()
    assert len(cats2) == 1 and cats2[0]["name"] == "C2"
