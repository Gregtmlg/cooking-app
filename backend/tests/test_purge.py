"""Compte « Système » et purge (4c J5b).

La purge est IRRÉVERSIBLE : seulement un profil déjà désactivé, avec le nom retapé,
vérifié par le serveur. Les recettes survivent à la personne, au profil Système.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.account import Account
from app.models.profile import Profile
from app.models.profile_group import profile_groups
from app.models.recipe import Recipe
from app.models.session import AuthSession
from app.services.account_service import (
    ProfileStillActive,
    PurgeConfirmationMismatch,
    add_profile,
    authenticate,
    create_account,
    deactivate_account,
    deactivate_profile,
    purge_account,
    purge_profile,
    reactivate_profile,
    reset_password,
)
from app.services.group_service import add_profile_to_group
from app.services.system_service import (
    SystemAccountMissing,
    SystemAccountProtected,
    get_system_profile,
)

PASSWORD = "motdepasse123"
ADMIN = "/api/v1/admin"


def _profiles(account):
    by_name = {p.display_name: p for p in account.profiles}
    return by_name["Michel"], by_name["Jeanne"]


def _recipe(db_session, owner, title="Tarte"):
    recipe = Recipe(title=title, instructions="…", owner_id=owner.id)
    db_session.add(recipe)
    db_session.commit()
    return recipe


# --- Le compte Système ---------------------------------------------------------------------


def test_only_one_system_account_is_allowed_by_the_database(db_session, system_account):
    db_session.add(Account(username="Autre-système", password_hash="!", is_system=True))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_many_ordinary_accounts_do_not_collide_on_the_partial_index(db_session, system_account):
    create_account(db_session, username="Un", password=PASSWORD)
    create_account(db_session, username="Deux", password=PASSWORD)  # deux is_system = faux


def test_system_account_cannot_log_in(db_session, system_account):
    assert authenticate(db_session, "Système", "!") is None
    assert not system_account.is_active  # profil désactivé en permanence


def test_system_profile_is_never_created_on_the_fly(db_session):
    with pytest.raises(SystemAccountMissing):
        get_system_profile(db_session)


@pytest.mark.parametrize(
    "operation",
    [
        lambda db, a: reset_password(db, "Système", "nouveau-mot-de-passe"),
        lambda db, a: add_profile(db, "Système", "Intrus"),
        lambda db, a: reactivate_profile(db, a.profiles[0]),
        lambda db, a: deactivate_profile(db, a.profiles[0]),
        lambda db, a: deactivate_account(db, a),
        lambda db, a: purge_profile(db, a.profiles[0], "Système"),
        lambda db, a: purge_account(db, a, "Système"),
    ],
    ids=[
        "reset",
        "add-profile",
        "reactivate",
        "deactivate",
        "deactivate-account",
        "purge",
        "purge-account",
    ],
)
def test_admin_operations_refuse_the_system_account(db_session, system_account, operation):
    with pytest.raises(SystemAccountProtected):
        operation(db_session, system_account)


def test_system_profile_cannot_join_a_group(db_session, system_account, chuteam_group):
    with pytest.raises(SystemAccountProtected):
        add_profile_to_group(db_session, system_account.profiles[0], "chuteam")


# --- Purge d'un profil ---------------------------------------------------------------------


def test_purge_refuses_an_active_profile(db_session, system_account, multi_profile_account):
    _, jeanne = _profiles(multi_profile_account)
    with pytest.raises(ProfileStillActive):
        purge_profile(db_session, jeanne, "Jeanne")


def test_purge_requires_the_exact_name(db_session, system_account, multi_profile_account):
    _, jeanne = _profiles(multi_profile_account)
    deactivate_profile(db_session, jeanne)
    for wrong in ["", "jeanne", "Michel"]:
        with pytest.raises(PurgeConfirmationMismatch):
            purge_profile(db_session, jeanne, wrong)
    assert db_session.get(Profile, jeanne.id) is not None  # rien n'a bougé


def test_purge_moves_recipes_to_system_and_keeps_their_audience(
    db_session, system_account, multi_profile_account, chuteam_group
):
    """Test EXPLICITE : SQLite n'applique pas les clés étrangères par défaut — un oubli
    de réattribution laisserait des owner_id orphelins sans aucune erreur."""
    michel, jeanne = _profiles(multi_profile_account)
    tarte = _recipe(db_session, jeanne)
    tarte.audience = [chuteam_group]
    gratin = _recipe(db_session, michel, "Gratin")
    db_session.commit()
    deactivate_profile(db_session, jeanne)

    result = purge_profile(db_session, jeanne, "Jeanne")

    system = system_account.profiles[0]
    assert result.recipes_reassigned == 1
    assert db_session.get(Recipe, tarte.id).owner_id == system.id
    assert [g.slug for g in db_session.get(Recipe, tarte.id).audience] == ["chuteam"]
    assert db_session.get(Recipe, gratin.id).owner_id == michel.id  # Michel intouché
    owners = set(db_session.scalars(select(Recipe.owner_id)).all())
    existing = set(db_session.scalars(select(Profile.id)).all())
    assert owners <= existing  # aucun propriétaire orphelin


def test_purge_removes_profile_memberships_and_sessions(
    db_session, system_account, multi_profile_account
):
    from app.services.session_service import create_session

    michel, jeanne = _profiles(multi_profile_account)
    create_session(db_session, multi_profile_account.id, profile_id=michel.id)
    deactivate_profile(db_session, jeanne)
    jeanne_id = jeanne.id

    result = purge_profile(db_session, jeanne, "Jeanne")

    assert result.account_deleted is False
    assert db_session.get(Profile, jeanne_id) is None
    memberships = db_session.execute(
        select(profile_groups).where(profile_groups.c.profile_id == jeanne_id)
    ).all()
    assert memberships == []
    assert len(db_session.scalars(select(AuthSession)).all()) == 1  # Michel reste connecté


def test_purging_the_last_profile_deletes_the_account_and_frees_the_username(
    db_session, system_account, account
):
    account.must_change_password = False
    louise = account.profiles[0]
    _recipe(db_session, louise)
    deactivate_profile(db_session, louise)
    account_id = account.id

    result = purge_profile(db_session, louise, "Louise")

    assert result.account_deleted is True
    assert db_session.get(Account, account_id) is None
    create_account(db_session, username="louise", password=PASSWORD)  # identifiant libéré


# --- Purge d'un compte ---------------------------------------------------------------------


def test_purge_account_requires_an_inactive_account(
    db_session, system_account, multi_profile_account
):
    _, jeanne = _profiles(multi_profile_account)
    deactivate_profile(db_session, jeanne)  # Michel encore actif
    with pytest.raises(ProfileStillActive):
        purge_account(db_session, multi_profile_account, "Famille")


def test_purge_account_removes_every_profile(db_session, system_account, multi_profile_account):
    michel, jeanne = _profiles(multi_profile_account)
    _recipe(db_session, michel)
    _recipe(db_session, jeanne, "Gratin")
    deactivate_account(db_session, multi_profile_account)

    with pytest.raises(PurgeConfirmationMismatch):
        purge_account(db_session, multi_profile_account, "Michel")
    result = purge_account(db_session, multi_profile_account, "Famille")

    assert result.account_deleted is True
    assert result.recipes_reassigned == 2
    assert sorted(result.profile_ids) == sorted([michel.id, jeanne.id])
    assert db_session.scalars(select(Account).where(Account.username == "Famille")).all() == []


# --- Back-office web -----------------------------------------------------------------------


def _events(app_logs, name):
    return [r for r in app_logs.records if r.getMessage() == name]


def test_admin_purges_a_profile_with_name_free_audit(
    admin_client, db_session, system_account, multi_profile_account, app_logs
):
    _, jeanne = _profiles(multi_profile_account)
    url = f"{ADMIN}/profiles/{jeanne.id}/purge"

    assert admin_client.post(url, json={"confirm": "Jeanne"}).status_code == 409  # actif
    admin_client.post(f"{ADMIN}/profiles/{jeanne.id}/deactivate")
    assert admin_client.post(url, json={"confirm": "jeanne"}).status_code == 422
    assert admin_client.post(url, json={}).status_code == 422  # confirmation obligatoire

    r = admin_client.post(url, json={"confirm": "Jeanne"})
    assert r.status_code == 200
    assert r.json()["account_deleted"] is False

    events = _events(app_logs, "admin.profile_purged")
    assert len(events) == 1
    assert events[0].target_profile_id == jeanne.id
    assert "Jeanne" not in str(vars(events[0]))  # on n'archive pas ce qu'on efface


def test_admin_purges_an_account(admin_client, system_account, multi_profile_account):
    admin_client.post(f"{ADMIN}/accounts/{multi_profile_account.id}/deactivate")
    r = admin_client.post(
        f"{ADMIN}/accounts/{multi_profile_account.id}/purge", json={"confirm": "Famille"}
    )
    assert r.status_code == 200
    assert r.json()["account_deleted"] is True


def test_admin_cannot_touch_the_system_account(admin_client, system_account):
    profile_id = system_account.profiles[0].id
    assert admin_client.post(f"{ADMIN}/profiles/{profile_id}/reactivate").status_code == 409
    r = admin_client.post(f"{ADMIN}/profiles/{profile_id}/purge", json={"confirm": "Système"})
    assert r.status_code == 409


def test_admin_can_reassign_a_recipe_to_and_from_system(
    admin_client, db_session, system_account, account
):
    recipe = _recipe(db_session, account.profiles[0])
    system_id = system_account.profiles[0].id
    url = f"{ADMIN}/recipes/{recipe.id}/owner"

    assert admin_client.put(url, json={"profile_id": system_id}).json()["owner_id"] == system_id
    back = admin_client.put(url, json={"profile_id": account.profiles[0].id})
    assert back.json()["owner_id"] == account.profiles[0].id


def test_inventory_flags_the_system_account(admin_client, system_account):
    accounts = admin_client.get(f"{ADMIN}/inventory").json()["accounts"]
    flags = {a["username"]: (a["is_system"], a["is_active"]) for a in accounts}
    assert flags["Système"] == (True, False)
    assert flags["Admin"] == (False, True)
