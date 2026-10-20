from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.profile import Profile
from app.models.session import AuthSession


class ProfileServiceError(Exception):
    """Erreur générique de sélection de profil."""


class ProfileNotFound(ProfileServiceError):
    """Le profil demandé n'existe pas."""


class AmbiguousProfile(ProfileServiceError):
    """Plusieurs profils correspondent : il faut préciser lequel."""


def select_profile(db: Session, auth_session: AuthSession, profile_id: int) -> Profile:
    """
    Sélectionne un profil pour la session donnée.

    Args:
        db: Session SQLAlchemy.
        auth_session: Session d'authentification de l'utilisateur.
        profile_id: ID du profil à sélectionner.

    Returns:
        Le profil sélectionné.

    Raises:
        ProfileNotFound: Si le profil n'existe pas ou n'appartient pas à l'utilisateur.
    """
    profile = db.get(Profile, profile_id)
    if profile is None or profile.account_id != auth_session.account_id:
        raise ProfileNotFound("Ce profil n'existe pas ou n'est pas accessible.")
    auth_session.profile_id = profile.id
    db.commit()
    return profile


def find_profile(db: Session, username: str, display_name: str | None = None) -> Profile:
    """Retrouve un profil par son compte et, si besoin, son nom affiché.

    `display_name` peut être omis quand le compte n'a qu'un profil.
    """
    account = db.scalar(select(Account).where(Account.username == username))
    if account is None:
        raise ProfileNotFound(f"Le compte {username} n'existe pas.")

    if display_name is None:
        candidates = account.profiles
    else:
        candidates = [p for p in account.profiles if p.display_name == display_name]

    if not candidates:
        raise ProfileNotFound(f"Aucun profil « {display_name} » dans le compte '{username}'.")
    if len(candidates) > 1:
        raise AmbiguousProfile(
            f"Le compte '{username}' a plusieurs profils correspondants : précisez lequel."
        )

    return candidates[0]
