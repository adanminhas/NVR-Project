def test_login_success(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "nope"})
    assert res.status_code == 401


def test_login_unknown_user(client):
    res = client.post("/api/auth/login", json={"username": "ghost", "password": "whatever"})
    assert res.status_code == 401


def test_me_requires_token(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_returns_user(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["username"] == "admin"
    assert body["is_admin"] is True


def test_invalid_token_is_rejected(client):
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401
