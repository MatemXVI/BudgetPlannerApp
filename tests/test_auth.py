from fastapi.testclient import TestClient


def register_and_login(client: TestClient, email: str = "alice@example.com", password: str = "Passw0rd!"):
    # register
    r = client.post("/api/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201, r.text
    # login
    r = client.post("/api/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return token


def test_register_login_me_success(client: TestClient):
    token = register_and_login(client)
    # me
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "alice@example.com"
    assert data["is_active"] is True


def test_register_same_email_returns_400(client: TestClient):
    email = "bob@example.com"
    pwd = "StrongPass123"
    r1 = client.post("/api/auth/register", json={"email": email, "password": pwd})
    assert r1.status_code == 201
    r2 = client.post("/api/auth/register", json={"email": email, "password": pwd})
    assert r2.status_code == 400
    assert r2.json().get("detail") in {"Email already registered"}


def test_me_requires_auth(client: TestClient):
    r = client.get("/api/auth/me")
    assert r.status_code == 401
