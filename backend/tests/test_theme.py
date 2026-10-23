"""Thème : arbitre unique (theme_for), choix du profil, exposition dans la session."""

import pytest

from app.services import group_service
from app.services.group_service import GroupNotFound, NotInGroup


def _slug(group):
    return group.slug if group else None


# --- Service : qui reçoit quel thème ------------------------------------------------


@pytest.mark.parametrize(
    ("who", "expected"),
    [
        ("admin", None),  # admin → neutre
        ("lambda", None),  # sans groupe → neutre
        ("fam", "famille"),
        ("chu", "chuteam"),
        ("multi", "famille"),  # défaut : le groupe le plus ancien (id le plus petit)
    ],
)
def test_theme_for_defaults(world, who, expected):
    assert _slug(group_service.theme_for(world[who])) == expected


def test_theme_options_are_ordered_by_id(world):
    assert [g.slug for g in group_service.theme_options(world["multi"])] == ["famille", "chuteam"]


def test_profile_choice_is_used(db_session, world):
    group_service.set_theme(db_session, world["multi"], "chuteam")
    assert _slug(group_service.theme_for(world["multi"])) == "chuteam"


def test_choice_reset_to_default(db_session, world):
    group_service.set_theme(db_session, world["multi"], "chuteam")
    group_service.set_theme(db_session, world["multi"], None)
    assert _slug(group_service.theme_for(world["multi"])) == "famille"


def test_stale_choice_falls_back_to_default(db_session, world):
    multi = world["multi"]
    group_service.set_theme(db_session, multi, "chuteam")
    group_service.remove_profile_from_group(db_session, multi, "chuteam")
    assert _slug(group_service.theme_for(multi)) == "famille"


def test_cannot_choose_group_not_member(db_session, world):
    with pytest.raises(NotInGroup):
        group_service.set_theme(db_session, world["fam"], "chuteam")


def test_cannot_choose_unknown_group(db_session, world):
    with pytest.raises(GroupNotFound):
        group_service.set_theme(db_session, world["fam"], "inconnu")


# --- API : la session expose le thème ; PUT /auth/theme ------------------------------


def test_me_exposes_theme(auth_client):
    data = auth_client.get("/api/v1/auth/me").json()
    # Louise est dans chuteam (fixture sans clé de thème ni libellé).
    assert data["theme"] == {"slug": "chuteam", "key": None, "brand": None}
    assert len(data["theme_options"]) == 1


def test_login_exposes_theme(client, db_session, account):
    account.must_change_password = False
    db_session.commit()
    data = client.post(
        "/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"}
    ).json()
    assert data["theme"]["slug"] == "chuteam"


def test_put_theme_codes(auth_client, db_session):
    from app.models.group import Group

    db_session.add(Group(slug="famille", name="Famille"))
    db_session.commit()
    url = "/api/v1/auth/theme"
    assert auth_client.put(url, json={"group": "famille"}).status_code == 403
    assert auth_client.put(url, json={"group": "inconnu"}).status_code == 422
    response = auth_client.put(url, json={"group": None})
    assert response.status_code == 200
    assert response.json()["theme"]["slug"] == "chuteam"
