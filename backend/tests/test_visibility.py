"""Matrice de visibilité : qui voit quelle recette (point d'application unique)."""

import pytest

from app.models.group import Group
from app.models.recipe import Recipe
from app.services import recipe_service
from app.services.account_service import create_account


@pytest.fixture
def world(db_session):
    """Deux groupes, six profils, quatre recettes — un petit monde complet."""
    famille = Group(slug="famille", name="Famille")
    chuteam = Group(slug="chuteam", name="ChuTeam")
    db_session.add_all([famille, chuteam])
    db_session.commit()

    def profile(username, *slugs, admin=False):
        account = create_account(
            db_session, username=username, password="motdepasse123", is_admin=admin
        )
        p = account.profiles[0]
        p.groups.extend(g for g in (famille, chuteam) if g.slug in slugs)
        db_session.commit()
        return p

    profiles = {
        "auteur": profile("auteur"),  # sans groupe : propriétaire des recettes
        "lambda": profile("lambda"),  # sans groupe
        "fam": profile("fam", "famille"),
        "chu": profile("chu", "chuteam"),
        "multi": profile("multi", "famille", "chuteam"),
        "admin": profile("admin", admin=True),
    }

    def recipe(title, *, visible_to_all=False, audience=()):
        r = Recipe(
            title=title,
            instructions="…",
            owner_id=profiles["auteur"].id,
            visible_to_all=visible_to_all,
            audience=list(audience),
        )
        db_session.add(r)
        return r

    recipe("tous", visible_to_all=True)
    recipe("famille", audience=[famille])
    recipe("chuteam", audience=[chuteam])
    recipe("privee")
    db_session.commit()
    return profiles


@pytest.mark.parametrize(
    ("who", "expected"),
    [
        ("auteur", {"tous", "famille", "chuteam", "privee"}),
        ("lambda", {"tous"}),
        ("fam", {"tous", "famille"}),
        ("chu", {"tous", "chuteam"}),
        ("multi", {"tous", "famille", "chuteam"}),
        ("admin", {"tous", "famille", "chuteam", "privee"}),
    ],
)
def test_visibility_matrix(db_session, world, who, expected):
    recipes = recipe_service.get_recipes(db_session, world[who])
    assert {r.title for r in recipes} == expected


def test_invisible_recipe_is_none_like_missing(db_session, world):
    privee = next(
        r for r in recipe_service.get_recipes(db_session, world["auteur"]) if r.title == "privee"
    )
    assert recipe_service.get_recipe(db_session, world["lambda"], privee.id) is None


def test_invisible_recipe_cannot_be_deleted(db_session, world):
    privee = next(
        r for r in recipe_service.get_recipes(db_session, world["auteur"]) if r.title == "privee"
    )
    assert recipe_service.delete_recipe(db_session, world["fam"], privee.id) is None
    assert recipe_service.get_recipe(db_session, world["auteur"], privee.id) == privee


def test_created_recipe_belongs_to_creator(auth_client):
    recipe_create = auth_client.post(
        "/api/v1/recipes/", json={"title": "Crêpes", "instructions": "Mélanger."}
    )
    recipe_id = recipe_create.json()["id"]
    assert auth_client.get(f"/api/v1/recipes/{recipe_id}").status_code == 200


def test_other_profile_gets_404_on_private_recipe(client, db_session, account, another_account):
    account.must_change_password = False
    another_account.must_change_password = False
    db_session.commit()

    client.post("/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"})
    recipe_create = client.post(
        "/api/v1/recipes/", json={"title": "Secret", "instructions": "Mélanger."}
    )
    secret_id = recipe_create.json()["id"]

    client.post("/api/v1/auth/login", json={"username": "Autre", "password": "motdepasse123"})

    assert client.get(f"/api/v1/recipes/{secret_id}").status_code == 404
    assert client.patch(f"/api/v1/recipes/{secret_id}", json={"title": "Volé"}).status_code == 404
    assert client.delete(f"/api/v1/recipes/{secret_id}").status_code == 404
