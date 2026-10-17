import pytest

from app.api.deps import PASSWORD_CHANGE_REQUIRED, PROFILE_REQUIRED

LOGIN_URL = "/api/v1/auth/login"
PROTECTED_URLS = ["/api/v1/recipes/", "/api/v1/ingredients/"]


def login(client, username):
    response = client.post(LOGIN_URL, json={"username": username, "password": "motdepasse123"})
    assert response.status_code == 200


@pytest.mark.parametrize("url", PROTECTED_URLS)
def test_anonymous_gets_401(client, url):
    assert client.get(url).status_code == 401


@pytest.mark.parametrize("url", PROTECTED_URLS)
def test_password_change_required(client, account, url):
    login(client, "Louise")
    response = client.get(url)
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == PASSWORD_CHANGE_REQUIRED


@pytest.mark.parametrize("url", PROTECTED_URLS)
def test_profile_required(client, db_session, multi_profile_account, url):
    multi_profile_account.must_change_password = False  # isoler le défaut « profil »
    db_session.commit()
    login(client, "Famille")
    response = client.get(url)
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == PROFILE_REQUIRED


def test_password_checked_before_profile(client, multi_profile_account):
    # Mot de passe provisoire ET aucun profil sélectionné : le mot de passe gagne.
    login(client, "Famille")
    response = client.get("/api/v1/recipes/")
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == PASSWORD_CHANGE_REQUIRED


@pytest.mark.parametrize("url", PROTECTED_URLS)
def test_authenticated_client_gets_200(auth_client, url):
    assert auth_client.get(url).status_code == 200
