"""Horloge unique de l'application.

UTC mais NAÏF (sans fuseau), pour rester comparable aux datetimes relus de SQLite
(dette assumée T4a J3, à revoir à la charnière PostgreSQL). Outil technique transverse :
il vit dans `core`, à la différence des règles métier qui vivent sur les modèles.
"""

from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
