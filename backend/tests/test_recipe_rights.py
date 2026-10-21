import pytest
from sqlalchemy import select

from app.models.recipe import Recipe
from app.schemas.recipe import RecipeUpdate
from app.services import recipe_service
from app.services.recipe_service import RecipeEditForbidden


def _recipe(db_session, title):
    return db_session.scalar(select(Recipe).where(Recipe.title == title))


@pytest.mark.parametrize(
    ("who", "expected"),
    [("auteur", True), ("admin", True), ("fam", False), ("multi", False)],
)
def test_can_edit_matrix(db_session, world, who, expected):
    famille = _recipe(db_session, "famille")
    assert recipe_service.can_edit(world[who], famille) is expected


def test_member_cannot_update_visible_recipe(db_session, world):
    famille = _recipe(db_session, "famille")
    with pytest.raises(RecipeEditForbidden):
        recipe_service.update_recipe(db_session, world["fam"], famille.id, RecipeUpdate(title="X"))
    assert famille.title == "famille"


def test_member_cannot_delete_visible_recipe(db_session, world):
    famille = _recipe(db_session, "famille")
    with pytest.raises(RecipeEditForbidden):
        recipe_service.delete_recipe(db_session, world["fam"], famille.id)


def test_admin_can_delete_any_recipe(db_session, world):
    privee = _recipe(db_session, "privee")
    assert recipe_service.delete_recipe(db_session, world["admin"], privee.id) is not None


def test_api_can_edit_and_403(client, db_session, account, another_account):
    account.must_change_password = False
    another_account.must_change_password = False
    db_session.commit()

    client.post("/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"})
    created = client.post("/api/v1/recipes/", json={"title": "Tarte", "instructions": "…"})
    assert created.json()["can_edit"] is True
    recipe_id = created.json()["id"]

    # Rendue visible à tous (le formulaire ne le permet qu'à partir de J4b).
    db_session.get(Recipe, recipe_id).visible_to_all = True
    db_session.commit()

    client.post("/api/v1/auth/login", json={"username": "Autre", "password": "motdepasse123"})
    response = client.get(f"/api/v1/recipes/{recipe_id}")
    assert response.status_code == 200
    assert response.json()["can_edit"] is False
    assert client.patch(f"/api/v1/recipes/{recipe_id}", json={"title": "X"}).status_code == 403
    assert client.delete(f"/api/v1/recipes/{recipe_id}").status_code == 403
