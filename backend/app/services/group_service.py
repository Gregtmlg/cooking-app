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


# --- Thème -------------------------------------------------------------------------


def theme_options(profile: Profile) -> list[Group]:
    """Thèmes entre lesquels ce profil peut choisir : ses groupes, par ancienneté (id).

    L'admin et les profils sans groupe n'ont pas de choix (thème neutre).
    """
    if profile.account.is_admin:
        return []
    return sorted(profile.groups, key=lambda group: group.id)


def theme_for(profile: Profile) -> Group | None:
    """ARBITRE UNIQUE du thème (principe 8). None → thème neutre.

    1. admin ou sans groupe → neutre ;
    2. choix du profil, s'il est TOUJOURS membre de ce groupe ;
    3. sinon le premier groupe par ancienneté (id) — jamais l'ordre d'insertion.
    """
    options = theme_options(profile)
    if not options:
        return None
    if profile.theme_group in options:
        return profile.theme_group
    return options[0]


def set_theme(db: Session, profile: Profile, group_slug: str | None) -> None:
    """Enregistre le choix de thème du profil (None → revenir au défaut)."""
    if group_slug is None:
        profile.theme_group = None
    else:
        group = get_group_by_slug(db, group_slug)
        if group not in theme_options(profile):
            raise NotInGroup(f"« {profile.display_name} » n'est pas dans le groupe '{group_slug}'.")
        profile.theme_group = group
    db.commit()
