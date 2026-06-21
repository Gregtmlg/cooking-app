from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="recipes")