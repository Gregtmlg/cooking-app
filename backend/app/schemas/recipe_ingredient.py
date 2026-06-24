from pydantic import BaseModel
from app.schemas.ingredient import IngredientRead

class RecipeIngredientBase(BaseModel):
    ingredient_name: str
    quantity: float | None = None   # Optionnel — peut être absent, vaut None si absent
    unit: str | None = None

class RecipeIngredientCreate(RecipeIngredientBase):
    pass

class RecipeIngredientRead(BaseModel):
    ingredient: IngredientRead
    quantity: float | None  # Obligatoire — doit être fourni, peut valoir None
    unit: str | None

    model_config = {"from_attributes": True}