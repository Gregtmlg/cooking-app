from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base

profile_groups = Table(
    "profile_groups",
    Base.metadata,
    Column("profile_id", Integer, ForeignKey("profiles.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
)
