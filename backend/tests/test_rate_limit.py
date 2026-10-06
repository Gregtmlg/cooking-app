
def test_login_rate_limited_after_5_attempts(client, account):
    # 5 tentatives (mauvais mot de passe) → toutes passent la garde (401)
    for _ in range(5):
        r = client.post("/api/v1/auth/login", json={"username": "Louise", "password": "faux"})
        assert r.status_code == 401
    # la 6e est bloquée par le rate-limiter
    r = client.post("/api/v1/auth/login", json={"username": "Louise", "password": "faux"})
    assert r.status_code == 429
