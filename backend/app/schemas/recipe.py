from datetime import datetime

from pydantic import BaseModel, model_validator

from app.schemas.group import GroupRead
from app.schemas.recipe_ingredient import RecipeIngredientCreate, RecipeIngredientRead


class RecipeBase(BaseModel):
    title: str
    description: str | None = None
    instructions: str
    prep_time: int | None = None
    cook_time: int | None = None
    servings: int | None = None


class RecipeCreate(RecipeBase):
    ingredients: list[RecipeIngredientCreate] = []  # liste vide par défaut si absent
    # "Tous" (True, []), groupes (False, [slugs])
    # "Moi uniquement" (False, [])

    visible_to_all: bool = False
    audience: list[str] = []

    @model_validator(mode="after")
    def check_audience(self):
        if self.visible_to_all and self.audience:
            raise ValueError("« Tous » ne se combine pas avec des groupes.")
        return self


class RecipeUpdate(RecipeBase):
    title: str | None = None
    description: str | None = None
    instructions: str | None = None
    prep_time: int | None = None
    cook_time: int | None = None
    servings: int | None = None
    ingredients: list[RecipeIngredientCreate] | None = (
        None  # None = None envoyé → pas de mise à jour des ingrédients
    )
    visible_to_all: bool | None = None
    audience: list[str] | None = None

    @model_validator(mode="after")
    def check_audience(self):
        # « Tout ou rien » : les deux champs voyagent ensemble, sinon l'état final
        # pourrait mélanger « Tous » et des groupes.
        if (self.visible_to_all is None) != (self.audience is None):
            raise ValueError("visible_to_all et audience doivent être envoyés ensemble.")
        if self.visible_to_all and self.audience:
            raise ValueError("« Tous » ne se combine pas avec des groupes.")
        return self


class RecipeRead(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    ingredients: (
        list[RecipeIngredientRead] | None
    )  # Obligatoire — doit être fourni, peut valoir None
    visible_to_all: bool
    audience: list[GroupRead]
    can_edit: bool = False  # champ calculé, pas en bdd : par défaut à False

    model_config = {"from_attributes": True}
