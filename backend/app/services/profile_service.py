from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.session import AuthSession


class ProfileServiceError(Exception):
    """Erreur générique de sélection de profil."""


class ProfileNotFound(ProfileServiceError):
    """Le profil demandé n'existe pas."""



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
