"""Dépendances injectables partagées par les routeurs.

Centraliser les alias ici évite de répéter `Depends(...)` dans chaque
signature, et fournit un point unique où ajouter les dépendances futures
(profil courant, permissions...).
"""
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.account import Account
from app.models.profile import Profile
from app.models.session import AuthSession
from app.services import session_service

# `Depends` est ici une ANNOTATION, non une valeur par défaut.
# Forme recommandée depuis FastAPI 0.95 — et B008 n'a plus lieu d'être.
DbSession = Annotated[Session, Depends(get_db)]

SESSION_COOKIE_NAME = "cooking_session"

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
            status_code=status.HTTP_403_FORBIDDEN, detail="Aucun profil sélectionné."
        )
    return auth_session.profile

CurrentProfile = Annotated[Profile, Depends(get_current_profile)]
