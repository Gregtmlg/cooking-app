from pydantic import BaseModel

class IngredientBase(BaseModel):
    name: str

class IngredientCreate(IngredientBase):
    pass

class IngredientRead(IngredientBase):
    id: int

    model_config = {"from_attributes": True}