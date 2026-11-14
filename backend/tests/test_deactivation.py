"""Désactivation des profils (4c J5a).

Seuls les profils portent un état ; un compte est actif tant qu'il lui reste un profil
actif (D1). Organisation : la règle (modèle) → le service → UNE SECTION PAR PORTE
(tableau du quiz J5a) → le back-office web.
"""

import pytest
from sqlalchemy import select

from app.models.account import Account
from app.models.profile import Profile
from app.models.session import AuthSession
from app.services.account_service import (
    LastAdminForbidden,
    MultiProfileChangeForbidden,
    ProfileAlreadyDeactivated,
    ProfileNameTaken,
    ProfileNotDeactivated,
    SelfDeactivationForbidden,
    add_profile,
    change_password,
    create_account,
    deactivate_account,
    deactivate_profile,
    reactivate_profile,
    reset_password,
)
from app.services.inventory_service import account_entry
from app.services.profile_service import ProfileNotFound, find_profile, select_profile
from app.services.session_service import _hash_token, create_session

LOGIN = "/api/v1/auth/login"
PASSWORD = "motdepasse123"


def _login(client, username):
    return client.post(LOGIN, json={"username": username, "password": PASSWORD})


def _profiles(account):
    """Michel et Jeanne du compte « Famille » (fixture multi_profile_account)."""
    by_name = {p.display_name: p for p in account.profiles}
    return by_name["Michel"], by_name["Jeanne"]


@pytest.fixture
def admin(db_session):
    account = create_account(db_session, username="Admin", password=PASSWORD, is_admin=True)
    account.must_change_password = False
    db_session.commit()
    return account


# --- La règle, sur le modèle (Python ET SQL) ---------------------------------------------


def test_profile_is_active_python_and_sql(db_session, multi_profile_account):
    michel, jeanne = _profiles(multi_profile_account)
    deactivate_profile(db_session, jeanne)

    assert michel.is_active and not jeanne.is_active
    active_ids = db_session.scalars(select(Profile.id).where(Profile.is_active)).all()
    assert michel.id in active_ids and jeanne.id not in active_ids


def test_account_state_is_derived_from_its_profiles(db_session, multi_profile_account):
    michel, jeanne = _profiles(multi_profile_account)
    active_accounts = select(Account.id).where(Account.is_active)

    deactivate_profile(db_session, jeanne)
    assert multi_profile_account.is_active  # Michel reste
    assert multi_profile_account.id in db_session.scalars(active_accounts).all()

    deactivate_profile(db_session, michel)  # le dernier emporte le compte
    assert not multi_profile_account.is_active
    assert multi_profile_account.id not in db_session.scalars(active_accounts).all()

    reactivate_profile(db_session, jeanne)  # réactiver un profil réactive le compte
    assert multi_profile_account.is_active
    assert multi_profile_account.active_profiles == [jeanne]


# --- Le service ----------------------------------------------------------------------------


def test_deactivate_sets_date_and_keeps_recipes_owner(db_session, world):
    from app.models.recipe import Recipe

    auteur = world["auteur"]
    deactivate_profile(db_session, auteur)

    assert auteur.deactivated_at is not None
    owners = db_session.scalars(select(Recipe.owner_id)).all()
    assert set(owners) == {auteur.id}  # bien commun : rien ne bouge


def test_deactivate_twice_and_reactivate_active_are_refused(db_session, account):
    with pytest.raises(ProfileNotDeactivated):
        reactivate_profile(db_session, account.profiles[0])
    account.must_change_password = False
    deactivate_profile(db_session, account.profiles[0])
    with pytest.raises(ProfileAlreadyDeactivated):
        deactivate_profile(db_session, account.profiles[0])


def test_deactivate_account_deactivates_every_active_profile(db_session, multi_profile_account):
    deactivate_account(db_session, multi_profile_account)
    assert all(not p.is_active for p in multi_profile_account.profiles)
    with pytest.raises(ProfileAlreadyDeactivated):
        deactivate_account(db_session, multi_profile_account)


# --- Anti-verrouillage ---------------------------------------------------------------------


def test_cannot_deactivate_oneself(db_session, multi_profile_account):
    michel, jeanne = _profiles(multi_profile_account)
    with pytest.raises(SelfDeactivationForbidden):
        deactivate_profile(db_session, michel, actor=michel)
    with pytest.raises(SelfDeactivationForbidden):  # le raccourci m'inclut aussi
        deactivate_account(db_session, multi_profile_account, actor=michel)
    assert michel.is_active and jeanne.is_active  # rien n'a bougé


def test_last_active_admin_is_protected_even_from_cli(db_session, admin):
    with pytest.raises(LastAdminForbidden):
        deactivate_profile(db_session, admin.profiles[0])  # actor=None : la CLI
    assert admin.is_active


def test_admin_can_be_deactivated_when_another_active_admin_exists(db_session, admin):
    create_account(db_session, username="Admin2", password=PASSWORD, is_admin=True)
    deactivate_profile(db_session, admin.profiles[0])
    assert not admin.is_active


def test_an_inactive_admin_does_not_count_as_a_spare(db_session, admin):
    spare = create_account(db_session, username="Admin2", password=PASSWORD, is_admin=True)
    deactivate_profile(db_session, spare.profiles[0])
    with pytest.raises(LastAdminForbidden):
        deactivate_profile(db_session, admin.profiles[0])


# --- Porte : login ------------------------------------------------------------------------


def test_inactive_account_cannot_log_in_with_generic_401(client, db_session, account):
    account.must_change_password = False
    deactivate_profile(db_session, account.profiles[0])

    response = _login(client, "Louise")
    wrong_password = client.post(LOGIN, json={"username": "Louise", "password": "mauvais-123"})

    assert response.status_code == 401
    assert response.json() == wrong_password.json()  # aucun indice : anti-énumération


# --- Porte : session déjà ouverte (la plus importante) ------------------------------------


def test_open_session_loses_access_when_last_profile_is_deactivated(
    auth_client, db_session, account
):
    assert auth_client.get("/api/v1/auth/me").status_code == 200
    deactivate_profile(db_session, account.profiles[0])

    assert auth_client.get("/api/v1/auth/me").status_code == 401
    assert auth_client.get("/api/v1/recipes/").status_code == 401
    assert db_session.scalars(select(AuthSession)).all() == []  # sessions révoquées


def test_d3_only_the_deactivated_profile_sessions_are_removed(db_session, multi_profile_account):
    michel, jeanne = _profiles(multi_profile_account)
    jeanne_token = create_session(db_session, multi_profile_account.id, profile_id=jeanne.id)
    michel_token = create_session(db_session, multi_profile_account.id, profile_id=michel.id)
    pending_token = create_session(db_session, multi_profile_account.id)  # sélection en attente

    deactivate_profile(db_session, jeanne)

    remaining = set(db_session.scalars(select(AuthSession.id)).all())
    assert _hash_token(jeanne_token) not in remaining
    assert {_hash_token(michel_token), _hash_token(pending_token)} <= remaining


def test_session_on_deactivated_profile_is_rejected_defense_in_depth(
    client, db_session, multi_profile_account
):
    """Même si une session survivait (état fabriqué), validate_session la refuse."""
    _, jeanne = _profiles(multi_profile_account)
    response = _login(client, "Famille")
    client.post("/api/v1/auth/select-profile", json={"profile_id": jeanne.id})
    jeanne.deactivated_at = jeanne.account.created_at  # sans passer par le service
    db_session.commit()

    assert response.status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


# --- Portes : sélection de profil -----------------------------------------------------------


def test_profile_list_shows_only_active_profiles(client, db_session, multi_profile_account):
    michel, jeanne = _profiles(multi_profile_account)
    deactivate_profile(db_session, jeanne)
    create_account(db_session, username="Bis", password=PASSWORD)  # bruit

    _login(client, "Famille")
    ids = [p["id"] for p in client.get("/api/v1/auth/profiles").json()]
    assert ids == [michel.id]


def test_deactivated_profile_cannot_be_selected_by_id(db_session, multi_profile_account):
    michel, jeanne = _profiles(multi_profile_account)
    auth_session = db_session.get(
        AuthSession, _hash_token(create_session(db_session, multi_profile_account.id))
    )
    deactivate_profile(db_session, jeanne)

    with pytest.raises(ProfileNotFound):
        select_profile(db_session, auth_session, jeanne.id)


def test_login_auto_selects_the_last_active_profile(client, db_session, multi_profile_account):
    michel, jeanne = _profiles(multi_profile_account)
    deactivate_profile(db_session, jeanne)

    body = _login(client, "Famille").json()
    assert body["profile"]["id"] == michel.id  # plus d'écran de sélection pour Michel


# --- Portes qui comptent TOUS les profils ---------------------------------------------------


def test_password_rules_still_count_deactivated_profiles(db_session, multi_profile_account):
    """D2 : un compte qui a été partagé le reste."""
    _, jeanne = _profiles(multi_profile_account)
    deactivate_profile(db_session, jeanne)

    assert reset_password(db_session, "Famille", "phrasedepasse").must_change_password is False
    multi_profile_account.must_change_password = True  # état fabriqué
    with pytest.raises(MultiProfileChangeForbidden):
        change_password(db_session, multi_profile_account, "phrasedepasse", "nouvelle-123")


def test_add_profile_name_still_reserved_by_deactivated_profile(db_session, multi_profile_account):
    _, jeanne = _profiles(multi_profile_account)
    deactivate_profile(db_session, jeanne)
    with pytest.raises(ProfileNameTaken):
        add_profile(db_session, "Famille", "jeanne")


def test_cli_finds_deactivated_profile_to_reactivate_it(db_session, multi_profile_account):
    _, jeanne = _profiles(multi_profile_account)
    deactivate_profile(db_session, jeanne)
    assert find_profile(db_session, "Famille", "Jeanne") is jeanne


def test_inventory_shows_state(db_session, multi_profile_account):
    _, jeanne = _profiles(multi_profile_account)
    deactivate_profile(db_session, jeanne)
    entry = account_entry(multi_profile_account)

    assert entry.is_active is True
    by_id = {p.id: p for p in entry.profiles}
    assert by_id[jeanne.id].deactivated_at is not None


# --- Back-office web ------------------------------------------------------------------------

ADMIN = "/api/v1/admin"


def _events(app_logs, name):
    return [r for r in app_logs.records if r.getMessage() == name]


def test_admin_deactivates_and_reactivates_profile(
    admin_client, db_session, multi_profile_account, app_logs
):
    _, jeanne = _profiles(multi_profile_account)

    r = admin_client.post(f"{ADMIN}/profiles/{jeanne.id}/deactivate")
    assert r.status_code == 200
    assert r.json()["deactivated_at"] is not None
    assert admin_client.post(f"{ADMIN}/profiles/{jeanne.id}/deactivate").status_code == 409

    r = admin_client.post(f"{ADMIN}/profiles/{jeanne.id}/reactivate")
    assert r.status_code == 200
    assert r.json()["deactivated_at"] is None

    assert len(_events(app_logs, "admin.profile_deactivated")) == 1
    assert len(_events(app_logs, "admin.profile_reactivated")) == 1
    refused = _events(app_logs, "admin.action_refused")
    assert [(e.action, e.status) for e in refused] == [("profile_deactivated", 409)]


def test_admin_deactivates_whole_account(admin_client, multi_profile_account, app_logs):
    r = admin_client.post(f"{ADMIN}/accounts/{multi_profile_account.id}/deactivate")
    assert r.status_code == 200
    body = r.json()
    assert body["is_active"] is False
    assert all(p["deactivated_at"] is not None for p in body["profiles"])
    assert len(_events(app_logs, "admin.account_deactivated")) == 1


def test_admin_cannot_deactivate_own_profile_via_web(admin_client, db_session):
    admin_profile = db_session.scalar(select(Profile).where(Profile.display_name == "Admin"))
    r = admin_client.post(f"{ADMIN}/profiles/{admin_profile.id}/deactivate")
    assert r.status_code == 409
    assert admin_profile.is_active


def test_unknown_profile_is_404(admin_client):
    assert admin_client.post(f"{ADMIN}/profiles/9999/deactivate").status_code == 404
    assert admin_client.post(f"{ADMIN}/profiles/9999/reactivate").status_code == 404
