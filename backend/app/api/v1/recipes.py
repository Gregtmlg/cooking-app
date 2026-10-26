import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentProfile, DbSession, get_current_profile, require_password_changed
from app.models.profile import Profile
from app.models.recipe import Recipe
from app.schemas.group import GroupRead
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate
from app.services import recipe_service
from app.services.group_service import GroupNotFound
from app.services.recipe_service import AudienceForbidden, RecipeEditForbidden

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    dependencies=[Depends(require_password_changed), Depends(get_current_profile)],
)


def _to_read(recipe: Recipe, profile: Profile) -> RecipeRead:
    """Sérialise une recette ET y ajoute les droits du profil courant."""

    read = RecipeRead.model_validate(recipe)
    read.can_edit = recipe_service.can_edit(profile, recipe)
    return read


@router.get("/", response_model=list[RecipeRead])
def list_recipes(
    db: DbSession,
    profile: CurrentProfile,
    skip: int = 0,
    limit: int = 100,
):
    recipes = recipe_service.get_recipes(db, profile, skip=skip, limit=limit)
    return [_to_read(recipe, profile) for recipe in recipes]


# ⚠️ Déclarée AVANT "/{recipe_id}" : sinon FastAPI tenterait de lire
# "audience-options" comme un identifiant entier (→ 422).
@router.get("/audience-options", response_model=list[GroupRead])
def get_audience_options(db: DbSession, profile: CurrentProfile):
    return recipe_service.audience_options(db, profile)


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(db: DbSession, profile: CurrentProfile, recipe_id: int):
    db_recipe = recipe_service.get_recipe(db, profile, recipe_id)
    if db_recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cette recette n'existe pas."
        )
    return _to_read(db_recipe, profile)


@router.post("/", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(
    db: DbSession,
    profile: CurrentProfile,
    recipe_in: RecipeCreate,
):
    try:
        db_recipe = recipe_service.create_recipe(db, profile, recipe_in)
    except AudienceForbidden as e:
        logger.warning(
            "recipe.audience_forbidden", extra={"profile_id": profile.id, "reason": str(e)}
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from None
    except GroupNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        ) from None
    return _to_read(db_recipe, profile)


@router.patch("/{recipe_id}", response_model=RecipeRead)
def update_recipe(db: DbSession, profile: CurrentProfile, recipe_id: int, recipe_in: RecipeUpdate):
    try:
        db_recipe = recipe_service.update_recipe(db, profile, recipe_id, recipe_in)
    except AudienceForbidden as e:
        logger.warning(
            "recipe.audience_forbidden",
            extra={"profile_id": profile.id, "recipe_id": recipe_id, "reason": str(e)},
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from None
    except RecipeEditForbidden as e:
        logger.warning(
            "recipe.edit_forbidden",
            extra={"profile_id": profile.id, "recipe_id": recipe_id, "reason": str(e)},
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from None
    except GroupNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        ) from None

    if db_recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cette recette n'existe pas."
        )
    return _to_read(db_recipe, profile)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(db: DbSession, profile: CurrentProfile, recipe_id: int):
    try:
        db_recipe = recipe_service.delete_recipe(db, profile, recipe_id)
    except RecipeEditForbidden as e:
        logger.warning(
            "recipe.edit_forbidden", extra={"profile_id": profile.id, "recipe_id": recipe_id}
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from None

    if db_recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cette recette n'existe pas."
        )
    return db_recipe
