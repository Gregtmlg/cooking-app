from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.profile_group import profile_groups

if TYPE_CHECKING:
    from app.models.profile import Profile


class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    theme: Mapped[str | None] = mapped_column(String(50), nullable=True)
    profiles: Mapped[list["Profile"]] = relationship(
        "Profile", secondary=profile_groups, back_populates="groups"
    )
