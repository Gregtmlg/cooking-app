"""Dépendances injectables partagées par les routeurs.

Centraliser les alias ici évite de répéter `Depends(...)` dans chaque
signature, et fournit un point unique où ajouter les dépendances futures
(profil courant, permissions...).
"""

import logging
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.account import Account
from app.models.profile import Profile
from app.models.session import AuthSession
from app.services import session_service

logger = logging.getLogger(__name__)

# `Depends` est ici une ANNOTATION, non une valeur par défaut.
# Forme recommandée depuis FastAPI 0.95 — et B008 n'a plus lieu d'être.
DbSession = Annotated[Session, Depends(get_db)]

SESSION_COOKIE_NAME = "cooking_session"
PROFILE_REQUIRED = "PROFILE_REQUIRED"
PASSWORD_CHANGE_REQUIRED = "PASSWORD_CHANGE_REQUIRED"


def get_current_session(
    db: DbSession,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> AuthSession:
    if session_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non authentifié.")
    auth_session = session_service.validate_session(db, session_token)
    if auth_session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalide.")
    return auth_session


CurrentSession = Annotated[AuthSession, Depends(get_current_session)]


def get_current_account(auth_session: CurrentSession) -> Account:
    return auth_session.account


CurrentAccount = Annotated[Account, Depends(get_current_account)]


def get_current_profile(auth_session: CurrentSession) -> Profile:
    if auth_session.profile is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": PROFILE_REQUIRED, "message": "Aucun profil sélectionné."},
        )
    return auth_session.profile


CurrentProfile = Annotated[Profile, Depends(get_current_profile)]


def require_password_changed(account: CurrentAccount) -> Account:
    if account.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": PASSWORD_CHANGE_REQUIRED,
                "message": "Vous devez d'abord changer votre mot de passe.",
            },
        )
    return account


PasswordChanged = Annotated[Account, Depends(require_password_changed)]


def require_admin(account: PasswordChanged, request: Request) -> Account:
    """Garde UNIQUE des routes admin : refus par défaut.

    Bâtie sur PasswordChanged (donc sur la session) : un admin au mot de passe
    provisoire est arrêté avant. Pas de `code` dans le 403 : l'intercepteur du
    front ne doit pas déclencher de resynchronisation pour un simple refus de droit.
    Un refus est JOURNALISÉ : l'interface n'y mène jamais, ce n'est donc pas un hasard.
    """
    if not account.is_admin:
        logger.warning(
            "auth.admin_forbidden",
            extra={
                "account_id": account.id,
                "username": account.username,
                "method": request.method,
                "path": request.url.path,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé à l'administrateur.",
        )
    return account


AdminAccount = Annotated[Account, Depends(require_admin)]
