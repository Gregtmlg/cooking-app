import pytest
from sqlalchemy import select

from app.models.recipe import Recipe
from app.services.recipe_service import (
    NewOwnerNotFound,
    ReassignForbidden,
    get_recipe,
    reassign_recipe,
)


def _recipe(db_session, title):
    return db_session.scalar(select(Recipe).where(Recipe.title == title))


def test_admin_reassigns_recipe(db_session, world):
    recipe = _recipe(db_session, "famille")
    updated = reassign_recipe(db_session, world["admin"], recipe.id, world["chu"].id)
    assert updated.owner_id == world["chu"].id  # type: ignore


def test_audience_is_unchanged(db_session, world):
    recipe = _recipe(db_session, "famille")
    reassign_recipe(db_session, world["admin"], recipe.id, world["chu"].id)
    assert [g.slug for g in recipe.audience] == ["famille"]
    assert recipe.visible_to_all is False


def test_new_owner_sees_recipe_outside_its_audience(db_session, world):
    """« chu » n'est pas dans Famille, mais un propriétaire voit toujours ses recettes."""
    recipe = _recipe(db_session, "famille")
    assert get_recipe(db_session, world["chu"], recipe.id) is None
    reassign_recipe(db_session, world["admin"], recipe.id, world["chu"].id)
    assert get_recipe(db_session, world["chu"], recipe.id) is not None


@pytest.mark.parametrize("actor", ["auteur", "fam", "multi"])
def test_non_admin_cannot_reassign_even_own_recipe(db_session, world, actor):
    recipe = _recipe(db_session, "tous")  # visible de tous, propriété d'« auteur »
    with pytest.raises(ReassignForbidden):
        reassign_recipe(db_session, world[actor], recipe.id, world["chu"].id)
    assert recipe.owner_id == world["auteur"].id


def test_unknown_recipe_returns_none(db_session, world):
    assert reassign_recipe(db_session, world["admin"], 9999, world["chu"].id) is None


def test_unknown_new_owner(db_session, world):
    recipe = _recipe(db_session, "famille")
    with pytest.raises(NewOwnerNotFound):
        reassign_recipe(db_session, world["admin"], recipe.id, 9999)
    assert recipe.owner_id == world["auteur"].id
