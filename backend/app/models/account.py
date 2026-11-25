from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Index, Integer, String, exists, false, func, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.core.identifiers import clean_username, username_key
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.profile import Profile
    from app.models.session import AuthSession


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        # UN SEUL compte Système, garanti par la base (J5b). Index unique PARTIEL : il ne
        # porte que sur les lignes is_system = vrai — un UNIQUE simple refuserait dès le
        # 2e compte ordinaire (doublon de « faux »). Déclaré ici, et pas seulement dans la
        # migration, pour que les tests (create_all) aient la même garantie.
        Index(
            "uq_accounts_single_system",
            "is_system",
            unique=True,
            sqlite_where=text("is_system = 1"),
            postgresql_where=text("is_system"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    # Clé d'unicité insensible à la casse — jamais écrite à la main (cf. _sync_username_key).
    username_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Compte « Système » (J5b) : réceptacle des recettes des profils purgés. Non
    # connectable (hash invalide + profil désactivé en permanence), hors de tout groupe,
    # intouchable par l'admin (cf. system_service.ensure_not_system).
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )
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

    # --- État DÉRIVÉ (J5a, décision D1) ----------------------------------------------
    # Aucune colonne d'état sur le compte : il est actif SI ET SEULEMENT SI il lui reste
    # au moins un profil actif. Une seule source de vérité → aucune désynchronisation.

    @property
    def active_profiles(self) -> list["Profile"]:
        """Profils actifs, triés par id (sélection, auto-sélection au login)."""
        return sorted((p for p in self.profiles if p.is_active), key=lambda p: p.id)

    @hybrid_property
    def is_active(self) -> bool:
        return any(p.is_active for p in self.profiles)

    @is_active.inplace.expression
    @classmethod
    def _is_active_expression(cls):
        from app.models.profile import Profile  # import local : évite le cycle de modules

        return exists().where(Profile.account_id == cls.id, Profile.is_active)
