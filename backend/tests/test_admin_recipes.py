"""J6b-2 — `GET /admin/recipes` : les recettes et leur propriétaire, pour l'onglet
Réattributions. Le refus d'un non-admin n'est pas réécrit ici : le filet OpenAPI du J2
(`test_every_admin_route_refuses_non_admin`) couvre d'office toute nouvelle route /admin.
"""

from sqlalchemy import select

from app.models.recipe import Recipe
from app.services.recipe_service import list_recipes_for_admin


def _recipe(db_session, title):
    return db_session.scalar(select(Recipe).where(Recipe.title == title))


def _login_world_admin(client, world, db_session):
    """L'admin du monde de test, mot de passe rendu définitif pour passer PasswordChanged."""
    world["admin"].account.must_change_password = False
    db_session.commit()
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "motdepasse123"})
    assert r.status_code == 200


def test_admin_sees_every_recipe_in_stable_order(db_session, world):
    titles = [r.title for r in list_recipes_for_admin(db_session, world["admin"])]
    # « privee » est en « Moi uniquement » chez « auteur » : l'admin la voit quand même.
    assert titles == ["tous", "famille", "chuteam", "privee"]


def test_non_admin_only_gets_what_it_already_sees(db_session, world):
    """Défense en profondeur : sans la garde du routeur, pas de fuite pour autant."""
    titles = [r.title for r in list_recipes_for_admin(db_session, world["lambda"])]
    assert titles == ["tous"]


def test_route_describes_owner(client, db_session, world):
    _login_world_admin(client, world, db_session)
    body = client.get("/api/v1/admin/recipes").json()
    privee = next(r for r in body if r["title"] == "privee")
    assert privee["owner"] == {
        "profile_id": world["auteur"].id,
        "display_name": "auteur",
        "account_username": "auteur",
        "is_system": False,
    }


def test_route_flags_system_owner(client, db_session, world, system_account):
    recipe = _recipe(db_session, "famille")
    recipe.owner_id = system_account.profiles[0].id
    db_session.commit()
    _login_world_admin(client, world, db_session)
    body = client.get("/api/v1/admin/recipes").json()
    owner = next(r for r in body if r["title"] == "famille")["owner"]
    assert owner["is_system"] is True
    assert owner["account_username"] == "Système"


def test_route_accepts_recipe_without_owner(client, db_session, world):
    """owner_id est nullable : une recette orpheline ne doit pas faire tomber la route (500)."""
    recipe = _recipe(db_session, "tous")
    recipe.owner_id = None
    db_session.commit()
    _login_world_admin(client, world, db_session)
    response = client.get("/api/v1/admin/recipes")
    assert response.status_code == 200
    assert next(r for r in response.json() if r["title"] == "tous")["owner"] is None
