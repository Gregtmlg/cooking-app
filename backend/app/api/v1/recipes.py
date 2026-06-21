from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.recipe import RecipeCreate, RecipeUpdate, RecipeRead
from app.services import recipe_service

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("/", response_model=list[RecipeRead])
def list_recipes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return recipe_service.get_recipes(db, skip=skip, limit=limit)

@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = recipe_service.get_recipe(db, recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cette recette n'existe pas.")
    return db_recipe

@router.post("/", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(recipe_in:RecipeCreate, db: Session = Depends(get_db)):
    return recipe_service.create_recipe(db, recipe_in)

@router.patch("/{recipe_id}", response_model=RecipeRead)
def update_recipe(recipe_id: int, recipe_in: RecipeUpdate, db: Session = Depends(get_db)):
    db_recipe = recipe_service.update_recipe(db, recipe_id, recipe_in)
    if db_recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cette recette n'existe pas.")
    return db_recipe

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db_recipe = recipe_service.delete_recipe(db, recipe_id)
    if db_recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cette recette n'existe pas.")
    return db_recipe