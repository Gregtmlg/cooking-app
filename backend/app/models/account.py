from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.core.identifiers import clean_username, username_key
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.profile import Profile
    from app.models.session import AuthSession


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    # Clé d'unicité insensible à la casse — jamais écrite à la main (cf. _sync_username_key).
    username_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    profiles: Mapped[list["Profile"]] = relationship(
        "Profile", back_populates="account", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["AuthSession"]] = relationship(
        "AuthSession", back_populates="account", cascade="all, delete-orphan"
    )

    @validates("username")
    def _sync_username_key(self, _key: str, value: str) -> str:
        cleaned_value = clean_username(value)
        self.username_key = username_key(cleaned_value)
        return cleaned_value
