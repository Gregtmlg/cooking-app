from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base

recipe_audience = Table(
    "recipe_audience",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
)
