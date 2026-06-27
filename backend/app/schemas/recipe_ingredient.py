from pydantic import BaseModel
from app.schemas.ingredient import IngredientRead

# RecipeIngredientCreate utilise ingredient_name (string) plutôt qu'un ingredient_id
# car le frontend travaille avec des noms. La résolution nom → ID est faite côté service.
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