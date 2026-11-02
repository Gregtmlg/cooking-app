"""Actions d'écriture du back-office : services branchés, erreurs traduites, audit signé."""

import pytest
from sqlalchemy import select

from app.models.account import Account
from app.models.recipe import Recipe

ADMIN = "/api/v1/admin"


def _account(db_session, username):
    return db_session.scalar(select(Account).where(Account.username == username))


# --- Création de compte --------------------------------------------------------------


def test_create_account(admin_client, db_session, chuteam_group):
    r = admin_client.post(
        f"{ADMIN}/accounts",
        json={"username": "Louise", "password": "motdepasse123", "group": "chuteam"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["username"] == "Louise"
    assert body["must_change_password"] is True
    assert body["is_admin"] is False
    assert body["profiles"][0]["groups"] == ["chuteam"]


def test_create_account_cannot_create_admin(admin_client, db_session):
    """`is_admin` n'existe pas dans le contrat : refusé bruyamment, pas ignoré."""
    r = admin_client.post(
        f"{ADMIN}/accounts",
        json={"username": "Pirate", "password": "motdepasse123", "is_admin": True},
    )
    assert r.status_code == 422
    assert _account(db_session, "Pirate") is None


def test_create_account_duplicate_is_409(admin_client, account):
    r = admin_client.post(f"{ADMIN}/accounts", json={"username": "LOUISE", "password": "x" * 8})
    assert r.status_code == 409


def test_create_account_short_password_is_422(admin_client):
    r = admin_client.post(f"{ADMIN}/accounts", json={"username": "Paul", "password": "court"})
    assert r.status_code == 422


def test_create_account_unknown_group_is_422(admin_client):
    r = admin_client.post(
        f"{ADMIN}/accounts",
        json={"username": "Paul", "password": "motdepasse123", "group": "inconnu"},
    )
    assert r.status_code == 422


# --- Réinitialisation ----------------------------------------------------------------


def test_reset_password(admin_client, db_session, account):
    from app.services.session_service import create_session

    account.must_change_password = False
    db_session.commit()
    create_session(db_session, account.id)

    r = admin_client.post(
        f"{ADMIN}/accounts/{account.id}/reset-password", json={"password": "provisoire123"}
    )
    assert r.status_code == 200
    assert r.json()["must_change_password"] is True
    assert r.json()["active_sessions"] == 0  # sessions de Louise révoquées


def test_reset_password_unknown_account_is_404(admin_client):
    r = admin_client.post(f"{ADMIN}/accounts/9999/reset-password", json={"password": "x" * 8})
    assert r.status_code == 404


# --- Ajout de profil -----------------------------------------------------------------


def test_add_profile(admin_client, db_session, account):
    account.must_change_password = False
    db_session.commit()
    r = admin_client.post(f"{ADMIN}/accounts/{account.id}/profiles", json={"display_name": "Paul"})
    assert r.status_code == 201
    assert r.json()["display_name"] == "Paul"


def test_add_profile_empty_name_is_422(admin_client, db_session, account):
    account.must_change_password = False
    db_session.commit()
    r = admin_client.post(f"{ADMIN}/accounts/{account.id}/profiles", json={"display_name": "  "})
    assert r.status_code == 422


def test_add_profile_while_provisional_is_409(admin_client, account):
    r = admin_client.post(f"{ADMIN}/accounts/{account.id}/profiles", json={"display_name": "Paul"})
    assert r.status_code == 409


# --- Appartenance aux groupes --------------------------------------------------------


def test_add_and_remove_group(admin_client, db_session, account):
    from app.models.group import Group

    db_session.add(Group(slug="famille", name="Famille"))
    db_session.commit()
    profile_id = account.profiles[0].id
    url = f"{ADMIN}/profiles/{profile_id}/groups/famille"

    r = admin_client.put(url)
    assert r.status_code == 200
    assert r.json()["groups"] == ["chuteam", "famille"]
    assert admin_client.put(url).status_code == 409  # déjà membre

    r = admin_client.delete(url)
    assert r.status_code == 200
    assert r.json()["groups"] == ["chuteam"]
    assert admin_client.delete(url).status_code == 409  # plus membre


@pytest.mark.parametrize("method", ["put", "delete"])
def test_group_unknown_slug_is_404(admin_client, account, method):
    url = f"{ADMIN}/profiles/{account.profiles[0].id}/groups/inconnu"
    assert getattr(admin_client, method)(url).status_code == 404


def test_group_unknown_profile_is_404(admin_client, chuteam_group):
    assert admin_client.put(f"{ADMIN}/profiles/9999/groups/chuteam").status_code == 404


# --- Réattribution -------------------------------------------------------------------


def test_reassign_recipe(admin_client, db_session, account, another_account):
    recipe = Recipe(title="Tarte", instructions="…", owner_id=account.profiles[0].id)
    db_session.add(recipe)
    db_session.commit()
    new_owner = another_account.profiles[0].id

    r = admin_client.put(f"{ADMIN}/recipes/{recipe.id}/owner", json={"profile_id": new_owner})
    assert r.status_code == 200
    assert r.json() == {"recipe_id": recipe.id, "owner_id": new_owner}


def test_reassign_unknown_recipe_is_404(admin_client, account):
    r = admin_client.put(f"{ADMIN}/recipes/9999/owner", json={"profile_id": account.profiles[0].id})
    assert r.status_code == 404


def test_reassign_unknown_owner_is_422(admin_client, db_session, account):
    recipe = Recipe(title="Tarte", instructions="…", owner_id=account.profiles[0].id)
    db_session.add(recipe)
    db_session.commit()
    r = admin_client.put(f"{ADMIN}/recipes/{recipe.id}/owner", json={"profile_id": 9999})
    assert r.status_code == 422


# --- Journal d'audit -----------------------------------------------------------------


def test_admin_action_is_audited_without_password(admin_client, app_logs):
    admin_client.post(f"{ADMIN}/accounts", json={"username": "Paul", "password": "secret-123"})

    events = [r for r in app_logs.records if r.getMessage() == "admin.account_created"]
    assert len(events) == 1
    assert events[0].actor_username == "Admin"
    assert events[0].target_username == "Paul"
    assert "secret-123" not in str(vars(events[0]))  # le mot de passe n'apparaît nulle part
