def test_login_sets_cookie(client, account):
    r = client.post("/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"})
    assert r.status_code == 200
    assert r.json()["username"] == "Louise"
    assert "cooking_session" in r.cookies

def test_login_wrong_password(client, account):
    r = client.post("/api/v1/auth/login", json={"username": "Louise", "password": "wrongpassword"})
    assert r.status_code == 401

def test_login_unknown_user(client):
    r = client.post("/api/v1/auth/login", json={"username": "Inconnu", "password": "motdepasse123"})
    assert r.status_code == 401

def test_me_requires_auth(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401

def test_me_after_login(client, account):
    client.post("/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"})
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == "Louise"

def test_logout(client, account):
    client.post("/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"})
    r = client.post("/api/v1/auth/logout")
    assert r.status_code == 204
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401
