from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.profile import Profile


class AuthSession(Base):
    __tablename__ = "sessions"

    # PK = SHA-256 (hex) du jeton ; le jeton en clair ne vit que dans le cookie.
    # Pas d'index= : une clé primaire est déjà indexée par la base.
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    # Indexée : la révocation filtre par compte (« toutes les sessions de X »).
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)
    # Renseignée à la sélection de profil (jalon 4). Pas d'index : aucun accès filtré prévu.
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("profiles.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    account: Mapped["Account"] = relationship("Account", back_populates="sessions")
    profile: Mapped["Profile | None"] = relationship("Profile")
