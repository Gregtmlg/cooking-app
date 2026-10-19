from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.recipe_audience import recipe_audience  # objet runtime, pas TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.profile import Profile
    from app.models.recipe_ingredient import RecipeIngredient


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    prep_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cook_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("profiles.id", name="fk_recipes_owner_id_profiles"), nullable=True, index=True
    )
    visible_to_all: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )
    owner: Mapped["Profile | None"] = relationship("Profile")
    audience: Mapped[list["Group"]] = relationship("Group", secondary=recipe_audience)
    ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        "RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan"
    )
