from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ingredient import IngredientRead
from app.services import recipe_service

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.get("/", response_model=list[IngredientRead])
def get_ingredients(db: Session = Depends(get_db)):
    return recipe_service.get_ingredients(db)