from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentProfile, DbSession, get_current_profile, require_password_changed
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate
from app.services import recipe_service

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    dependencies=[Depends(require_password_changed), Depends(get_current_profile)],
)


@router.get("/", response_model=list[RecipeRead])
def list_recipes(
    db: DbSession,
    profile: CurrentProfile,
    skip: int = 0,
    limit: int = 100,
):
    return recipe_service.get_recipes(db, profile, skip=skip, limit=limit)


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(db: DbSession, profile: CurrentProfile, recipe_id: int):
    db_recipe = recipe_service.get_recipe(db, profile, recipe_id)
    if db_recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cette recette n'existe pas."
        )
    return db_recipe


@router.post("/", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(
    db: DbSession,
    profile: CurrentProfile,
    recipe_in: RecipeCreate,
):
    return recipe_service.create_recipe(db, profile, recipe_in)


@router.patch("/{recipe_id}", response_model=RecipeRead)
def update_recipe(db: DbSession, profile: CurrentProfile, recipe_id: int, recipe_in: RecipeUpdate):
    db_recipe = recipe_service.update_recipe(db, profile, recipe_id, recipe_in)
    if db_recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cette recette n'existe pas."
        )
    return db_recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(db: DbSession, profile: CurrentProfile, recipe_id: int):
    db_recipe = recipe_service.delete_recipe(db, profile, recipe_id)
    if db_recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cette recette n'existe pas."
        )
    return db_recipe
