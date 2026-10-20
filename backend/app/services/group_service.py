from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.group import Group
from app.models.profile import Profile


class GroupServiceError(Exception):
    "Erreur dans la gestion des groupes."


class GroupNotFound(GroupServiceError): ...


class AlreadyInGroup(GroupServiceError): ...


class NotInGroup(GroupServiceError): ...


def get_group_by_slug(db: Session, slug: str) -> Group:
    group = db.scalar(select(Group).where(Group.slug == slug))  # None si absent

    if group is None:
        raise GroupNotFound(f"Le groupe {slug} n'existe pas.")

    return group


def add_profile_to_group(db: Session, profile: Profile, group_slug: str) -> Group:
    group = get_group_by_slug(db, group_slug)

    if group in profile.groups:
        raise AlreadyInGroup(f"{profile.display_name} est déjà dans le groupe {group.name}.")

    profile.groups.append(group)
    db.commit()

    return group


def remove_profile_from_group(db: Session, profile: Profile, group_slug: str) -> Group:
    group = get_group_by_slug(db, group_slug)

    if group not in profile.groups:
        raise NotInGroup(f"{profile.display_name} n'est pas dans le group {group.name}.")

    profile.groups.remove(group)
    db.commit()

    return group
