from pydantic import BaseModel
from app.schemas.ingredient import IngredientRead

class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    quantity: float | None = None
    unit: str | None = None

class RecipeIngredientCreate(RecipeIngredientBase):
    pass

class RecipeIngredientRead(BaseModel):
    ingredient: IngredientRead
    quantity: float | None
    unit: str | None

    model_config = {"from_attributes": True}