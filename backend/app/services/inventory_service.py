from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.group import Group
from app.services.group_service import theme_for
from app.services.session_service import active_session_count


@dataclass(frozen=True)
class ProfileEntry:
    id: int
    display_name: str
    groups: list[str]
    theme: str | None


@dataclass(frozen=True)
class AccountEntry:
    id: int
    username: str
    is_admin: bool
    must_change_password: bool
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


def get_inventory(db: Session) -> Inventory:
    accounts = db.scalars(select(Account).order_by(Account.id)).all()
    groups = db.scalars(select(Group).order_by(Group.id)).all()

    account_inventory = []
    for a in accounts:
        profile_inventory = []
        for p in sorted(a.profiles, key=lambda p: p.id):
            profile_inventory.append(
                ProfileEntry(
                    id=p.id,
                    display_name=p.display_name,
                    groups=[g.slug for g in sorted(p.groups, key=lambda g: g.id)],
                    theme=(t.slug if (t := theme_for(p)) else None),
                )
            )
        account_inventory.append(
            AccountEntry(
                id=a.id,
                username=a.username,
                is_admin=a.is_admin,
                must_change_password=a.must_change_password,
                created_at=a.created_at,
                active_sessions=active_session_count(a),
                profiles=profile_inventory,
            )
        )

    group_inventory = []
    for g in groups:
        group_inventory.append(GroupEntry(slug=g.slug, name=g.name, members=len(g.profiles)))

    return Inventory(accounts=account_inventory, groups=group_inventory)
