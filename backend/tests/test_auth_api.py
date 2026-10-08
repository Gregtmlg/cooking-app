def test_login_sets_cookie(client, account):
    r = client.post("/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"})
    assert r.status_code == 200
    assert r.json()["account"]["username"] == "Louise"
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
    assert r.json()["account"]["username"] == "Louise"


def test_me_reports_auto_selected_profile(client, account):
    client.post("/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"})
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["profile"]["id"] == account.profiles[0].id


def test_me_profile_null_until_selected(client, multi_profile_account):
    client.post("/api/v1/auth/login", json={"username": "Famille", "password": "motdepasse123"})
    assert client.get("/api/v1/auth/me").json()["profile"] is None

    target = multi_profile_account.profiles[1]
    client.post("/api/v1/auth/select-profile", json={"profile_id": target.id})
    assert client.get("/api/v1/auth/me").json()["profile"]["id"] == target.id


def test_logout(client, account):
    client.post("/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"})
    r = client.post("/api/v1/auth/logout")
    assert r.status_code == 204
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401
