"""Audience en entrée/sortie : validation, droits de publication, options."""

import pytest
from sqlalchemy import select

from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeUpdate
from app.services import recipe_service
from app.services.group_service import GroupNotFound
from app.services.recipe_service import AudienceForbidden


def _new(audience=(), visible_to_all=False):
    return RecipeCreate(
        title="R", instructions="…", visible_to_all=visible_to_all, audience=list(audience)
    )


def _slugs(recipe):
    return {group.slug for group in recipe.audience}


# --- Service : droits de publication -------------------------------------------------


def test_member_publishes_for_own_group(db_session, world):
    recipe = recipe_service.create_recipe(db_session, world["fam"], _new(["famille"]))
    assert _slugs(recipe) == {"famille"}


def test_member_cannot_publish_for_other_group(db_session, world):
    with pytest.raises(AudienceForbidden):
        recipe_service.create_recipe(db_session, world["fam"], _new(["chuteam"]))


def test_admin_publishes_for_any_group(db_session, world):
    recipe = recipe_service.create_recipe(db_session, world["admin"], _new(["chuteam"]))
    assert _slugs(recipe) == {"chuteam"}


def test_unknown_group_raises(db_session, world):
    with pytest.raises(GroupNotFound):
        recipe_service.create_recipe(db_session, world["fam"], _new(["inconnu"]))


def test_duplicate_slugs_are_merged(db_session, world):
    recipe = recipe_service.create_recipe(db_session, world["multi"], _new(["famille", "famille"]))
    assert len(recipe.audience) == 1


def test_owner_keeps_group_he_left(db_session, world):
    # « auteur » n'est dans aucun groupe, mais sa recette « famille » peut garder son audience.
    famille = db_session.scalar(select(Recipe).where(Recipe.title == "famille"))
    update = RecipeUpdate(title="Nouveau titre", visible_to_all=False, audience=["famille"])
    recipe = recipe_service.update_recipe(db_session, world["auteur"], famille.id, update)
    assert _slugs(recipe) == {"famille"}


def test_owner_cannot_add_group_he_is_not_in(db_session, world):
    famille = db_session.scalar(select(Recipe).where(Recipe.title == "famille"))
    update = RecipeUpdate(visible_to_all=False, audience=["famille", "chuteam"])
    with pytest.raises(AudienceForbidden):
        recipe_service.update_recipe(db_session, world["auteur"], famille.id, update)


@pytest.mark.parametrize(
    ("who", "expected"),
    [
        ("lambda", []),
        ("fam", ["famille"]),
        ("multi", ["chuteam", "famille"]),
        ("admin", ["chuteam", "famille"]),
    ],
)
def test_audience_options(db_session, world, who, expected):
    options = recipe_service.audience_options(db_session, world[who])
    assert [group.slug for group in options] == expected


# --- Schémas : validation (422) -------------------------------------------------------


def test_all_with_groups_is_rejected(auth_client):
    payload = {"title": "R", "instructions": "…", "visible_to_all": True, "audience": ["chuteam"]}
    assert auth_client.post("/api/v1/recipes/", json=payload).status_code == 422


def test_patch_audience_alone_is_rejected(auth_client):
    created = auth_client.post("/api/v1/recipes/", json={"title": "R", "instructions": "…"})
    response = auth_client.patch(
        f"/api/v1/recipes/{created.json()['id']}", json={"audience": ["chuteam"]}
    )
    assert response.status_code == 422


# --- API : codes et forme de la réponse -----------------------------------------------


def test_api_create_with_audience(auth_client):
    # Louise est membre de chuteam (fixture account).
    payload = {"title": "R", "instructions": "…", "visible_to_all": False, "audience": ["chuteam"]}
    data = auth_client.post("/api/v1/recipes/", json=payload).json()
    assert data["visible_to_all"] is False
    assert data["audience"] == [{"slug": "chuteam", "name": "ChuTeam"}]


def test_api_forbidden_and_unknown_group(auth_client, db_session):
    from app.models.group import Group

    db_session.add(Group(slug="famille", name="Famille"))
    db_session.commit()
    base = {"title": "R", "instructions": "…", "visible_to_all": False}
    response = auth_client.post("/api/v1/recipes/", json={**base, "audience": ["famille"]})
    assert response.status_code == 403
    response = auth_client.post("/api/v1/recipes/", json={**base, "audience": ["inconnu"]})
    assert response.status_code == 422


def test_api_audience_options_route(auth_client):
    response = auth_client.get("/api/v1/recipes/audience-options")
    assert response.status_code == 200
    assert response.json() == [{"slug": "chuteam", "name": "ChuTeam"}]


def test_api_patch_forbidden_group(auth_client, db_session):
    from app.models.group import Group

    db_session.add(Group(slug="famille", name="Famille"))
    db_session.commit()
    created = auth_client.post("/api/v1/recipes/", json={"title": "R", "instructions": "…"})
    response = auth_client.patch(
        f"/api/v1/recipes/{created.json()['id']}",
        json={"visible_to_all": False, "audience": ["famille"]},
    )
    assert response.status_code == 403


def test_api_patch_unknown_group(auth_client):
    created = auth_client.post("/api/v1/recipes/", json={"title": "R", "instructions": "…"})
    response = auth_client.patch(
        f"/api/v1/recipes/{created.json()['id']}",
        json={"visible_to_all": False, "audience": ["inconnu"]},
    )
    assert response.status_code == 422
