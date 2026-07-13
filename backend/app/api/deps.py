"""Dépendances injectables partagées par les routeurs.

Centraliser les alias ici évite de répéter `Depends(...)` dans chaque
signature, et fournit un point unique où ajouter les dépendances futures
(profil courant, permissions...).
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

# `Depends` est ici une ANNOTATION, non une valeur par défaut.
# Forme recommandée depuis FastAPI 0.95 — et B008 n'a plus lieu d'être.
DbSession = Annotated[Session, Depends(get_db)]
