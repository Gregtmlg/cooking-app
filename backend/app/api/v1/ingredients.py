from fastapi import APIRouter, Depends

from app.api.deps import DbSession, get_current_profile, require_password_changed
from app.schemas.ingredient import IngredientRead
from app.services import recipe_service

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"],
    dependencies=[Depends(require_password_changed), Depends(get_current_profile)],
)


@router.get("/", response_model=list[IngredientRead])
def get_ingredients(db: DbSession):
    return recipe_service.get_ingredients(db)
