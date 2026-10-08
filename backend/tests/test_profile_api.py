
def test_get_auth_profiles(client, multi_profile_account):
    client.post("/api/v1/auth/login", json={"username": "Famille", "password": "motdepasse123"})
    r = client.get("/api/v1/auth/profiles")
    assert r.status_code == 200
    names = {p["display_name"] for p in r.json()}
    assert names == {"Michel", "Jeanne"}

def test_profile_requires_auth(client):
    r = client.get("/api/v1/auth/profiles")
    assert r.status_code == 401

def test_select_profile_success(client, multi_profile_account):
    client.post("/api/v1/auth/login", json={"username": "Famille", "password": "motdepasse123"})
    target = multi_profile_account.profiles[0]
    r = client.post("/api/v1/auth/select-profile", json={"profile_id": target.id})
    assert r.status_code == 200
    assert r.json()["id"] == target.id

def test_profile_rejects_other_account(client, multi_profile_account, account):
    # 'account' est un autre compte (Louise) ; on tente de sélectionner son profil
    client.post("/api/v1/auth/login", json={"username": "Famille", "password": "motdepasse123"})
    foreign = account.profiles[0]
    r = client.post("/api/v1/auth/select-profile", json={"profile_id": foreign.id})
    assert r.status_code == 404

def test_login_single_profile_auto_selects(client, account, db_session):
    from app.models.session import AuthSession
    from app.services.session_service import _hash_token

    r = client.post("/api/v1/auth/login",
                    json={"username": "Louise", "password": "motdepasse123"})
    assert r.status_code == 200
    token = r.cookies["cooking_session"]
    session = db_session.get(AuthSession, _hash_token(token))
    assert session.profile_id == account.profiles[0].id   # profil déjà posé


def test_login_multi_profile_no_auto_select(client, multi_profile_account, db_session):
    from app.models.session import AuthSession
    from app.services.session_service import _hash_token

    r = client.post("/api/v1/auth/login",
                    json={"username": "Famille", "password": "motdepasse123"})
    token = r.cookies["cooking_session"]
    session = db_session.get(AuthSession, _hash_token(token))
    assert session.profile_id is None   # multi-profil → pas d'auto-sélection
