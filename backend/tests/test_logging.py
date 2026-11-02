def test_login_failed_is_logged(client, app_logs):
    client.post("/api/v1/auth/login", json={"username": "Inconnu", "password": "motdepasse123"})
    records = [r for r in app_logs.records if r.getMessage() == "auth.login_failed"]
    assert len(records) == 1
    assert records[0].username == "Inconnu"
