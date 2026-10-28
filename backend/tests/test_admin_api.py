import pytest

from app.api.deps import PASSWORD_CHANGE_REQUIRED
from app.services.account_service import create_account

INVENTORY_URL = "/api/v1/admin/inventory"


@pytest.fixture
def admin_client(client, db_session):
    admin = create_account(db_session, username="Admin", password="motdepasse123", is_admin=True)
    admin.must_change_password = False
    db_session.commit()
    response = client.post(
        "/api/v1/auth/login", json={"username": "Admin", "password": "motdepasse123"}
    )
    assert response.status_code == 200
    return client


def test_anonymous_gets_401(client):
    assert client.get(INVENTORY_URL).status_code == 401


def test_non_admin_gets_403(auth_client):
    assert auth_client.get(INVENTORY_URL).status_code == 403


def test_admin_with_provisional_password_is_stopped_first(client, db_session):
    create_account(db_session, username="Admin", password="motdepasse123", is_admin=True)
    client.post("/api/v1/auth/login", json={"username": "Admin", "password": "motdepasse123"})
    response = client.get(INVENTORY_URL)
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == PASSWORD_CHANGE_REQUIRED


def test_admin_reads_inventory(admin_client):
    response = admin_client.get(INVENTORY_URL)
    assert response.status_code == 200
    body = response.json()
    assert [a["username"] for a in body["accounts"]] == ["Admin"]
    assert body["accounts"][0]["is_admin"] is True
    assert body["accounts"][0]["active_sessions"] == 1  # la session du login


def test_every_admin_route_refuses_non_admin(auth_client):
    """Filet structurel, boîte noire : TOUTE route /admin publiée dans l'OpenAPI
    refuse un non-admin — y compris celles qu'on ajoutera plus tard."""
    paths = auth_client.app.openapi()["paths"]
    admin_routes = [
        (method, path.replace("{", "").replace("}", ""))  # paramètres → valeur bidon
        for path, methods in paths.items()
        if path.startswith("/api/v1/admin")
        for method in methods
    ]
    assert admin_routes  # sinon le test passerait à vide
    for method, path in admin_routes:
        response = auth_client.request(method.upper(), path)
        assert response.status_code == 403, f"{method.upper()} {path} → {response.status_code}"
