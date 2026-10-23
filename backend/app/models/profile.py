from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.profile_group import profile_groups  # objet runtime, pas TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.group import Group


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    account: Mapped["Account"] = relationship("Account", back_populates="profiles")
    groups: Mapped[list["Group"]] = relationship(
        "Group", secondary=profile_groups, back_populates="profiles"
    )
    # Thème choisi par le profil (multi-groupes). None → défaut (cf. theme_for).
    # FK NOMMÉE : obligatoire en batch mode SQLite (leçon J2a).
    theme_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("groups.id", name="fk_profiles_theme_group_id_groups"), nullable=True
    )
    theme_group: Mapped["Group | None"] = relationship("Group", foreign_keys=[theme_group_id])
