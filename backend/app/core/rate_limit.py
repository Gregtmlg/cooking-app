import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

RATE_LIMIT_MAX_ATTEMPTS = 5
RATE_LIMIT_WINDOW_SECONDS = 60

_attempts: dict[str, list[float]] = defaultdict(list)


def _client_ip(request: Request) -> str:
    """Retourne l'IP du client, ou une chaîne vide si introuvable."""
    return request.headers.get("CF-Connecting-IP") or request.client.host


def rate_limit_login(request: Request) -> None:
    """Lève une exception si le client a dépassé le nombre de tentatives autorisées."""
    ip = _client_ip(request)
    now = time.monotonic()

    # Fenêtre glissante : on ne garde que les tentatives des WINDOW dernières secondes.
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    _attempts[ip] = [t for t in _attempts[ip] if t > cutoff]

    if len(_attempts[ip]) >= RATE_LIMIT_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives de connexion. Veuillez réessayer dans une minute",
        )

    _attempts[ip].append(now)
