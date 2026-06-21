from pydantic import BaseModel
from app.schemas.recipe_ingredient import RecipeIngredientRead, RecipeIngredientCreate
from datetime import datetime

class RecipeBase(BaseModel):
    title: str
    description: str | None = None
    instructions: str
    prep_time: int | None = None
    cook_time: int | None = None
    servings: int | None = None

class RecipeCreate(RecipeBase):
    ingredients: list[RecipeIngredientCreate] = []

class RecipeUpdate(RecipeBase):
    title: str | None = None
    description: str | None = None
    instructions: str |None = None
    prep_time: int | None = None
    cook_time: int | None = None
    servings: int | None = None
    ingredients: list[RecipeIngredientCreate] | None = None

class RecipeRead(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    ingredients: list[RecipeIngredientRead] | None
    
    model_config = {"from_attributes": True}