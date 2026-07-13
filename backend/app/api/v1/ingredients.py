from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas.ingredient import IngredientRead
from app.services import recipe_service

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.get("/", response_model=list[IngredientRead])
def get_ingredients(db: DbSession):
    return recipe_service.get_ingredients(db)
