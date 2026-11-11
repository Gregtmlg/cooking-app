from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.group import Group
from app.models.profile import Profile
from app.services.group_service import theme_for
from app.services.session_service import active_session_count


@dataclass(frozen=True)
class ProfileEntry:
    id: int
    display_name: str
    groups: list[str]
    theme: str | None
    deactivated_at: datetime | None  # None = actif (J5a)


@dataclass(frozen=True)
class AccountEntry:
    id: int
    username: str
    is_admin: bool
    must_change_password: bool
    is_active: bool  # dérivé : au moins un profil actif (J5a)
    created_at: datetime
    active_sessions: int
    profiles: list[ProfileEntry]


@dataclass(frozen=True)
class GroupEntry:
    slug: str
    name: str
    members: int


@dataclass(frozen=True)
class Inventory:
    accounts: list[AccountEntry]
    groups: list[GroupEntry]


def profile_entry(p: Profile) -> ProfileEntry:
    """Constat d'un profil (réutilisé par l'inventaire ET les réponses des actions admin)."""
    return ProfileEntry(
        id=p.id,
        display_name=p.display_name,
        groups=[g.slug for g in sorted(p.groups, key=lambda g: g.id)],
        theme=(t.slug if (t := theme_for(p)) else None),
        deactivated_at=p.deactivated_at,
    )


def account_entry(a: Account) -> AccountEntry:
    """Constat d'un compte et de ses profils."""
    return AccountEntry(
        id=a.id,
        username=a.username,
        is_admin=a.is_admin,
        must_change_password=a.must_change_password,
        is_active=a.is_active,
        created_at=a.created_at,
        active_sessions=active_session_count(a),
        profiles=[profile_entry(p) for p in sorted(a.profiles, key=lambda p: p.id)],
    )


def get_inventory(db: Session) -> Inventory:
    accounts = db.scalars(select(Account).order_by(Account.id)).all()
    groups = db.scalars(select(Group).order_by(Group.id)).all()
    return Inventory(
        accounts=[account_entry(a) for a in accounts],
        groups=[GroupEntry(slug=g.slug, name=g.name, members=len(g.profiles)) for g in groups],
    )
