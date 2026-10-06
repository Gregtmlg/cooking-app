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
from app.services import session_service

# `Depends` est ici une ANNOTATION, non une valeur par défaut.
# Forme recommandée depuis FastAPI 0.95 — et B008 n'a plus lieu d'être.
DbSession = Annotated[Session, Depends(get_db)]

SESSION_COOKIE_NAME = "cooking_session"


def get_current_account(
    db: DbSession,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> Account:
    if session_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Non authentifié.")
    auth_session = session_service.validate_session(db, session_token)
    if auth_session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalide.")
    return auth_session.account


CurrentAccount = Annotated[Account, Depends(get_current_account)]
