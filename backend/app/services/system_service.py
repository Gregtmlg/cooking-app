"""Compte « Système » (4c J5b) : tombstone des profils purgés.

Module à part, sans dépendance vers les autres services : `account_service` ET
`group_service` l'importent pour leurs gardes, sans cycle d'imports.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.profile import Profile

SYSTEM_DISPLAY_NAME = "Système"


class SystemAccountProtected(Exception):
    """Une opération d'administration vise le compte Système : refusée."""


class SystemAccountMissing(RuntimeError):
    """Le compte Système n'existe pas : migration non appliquée. Bug d'exploitation (500)."""


def ensure_not_system(account: Account) -> None:
    """GARDE UNIQUE : appelée par chaque opération d'admin qui vise un compte ou un profil."""
    if account.is_system:
        raise SystemAccountProtected("Le compte Système ne peut pas être modifié.")


def get_system_profile(db: Session) -> Profile:
    """Le profil Système. Ne le CRÉE JAMAIS : sa naissance appartient à la migration
    (dev, prod) ou à la fixture (tests). Une création « au cas où » masquerait une
    migration manquante."""
    profile = db.scalar(select(Profile).join(Account).where(Account.is_system))
    if profile is None:
        raise SystemAccountMissing(
            "Compte Système introuvable : la migration n'a pas été appliquée (alembic upgrade)."
        )
    return profile
