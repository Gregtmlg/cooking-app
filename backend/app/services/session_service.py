import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.session import AuthSession

SESSION_LIFETIME = timedelta(days=14)


def _utcnow() -> datetime:
    # UTC mais naïf, pour rester comparable aux datetimes relus de SQLite.
    return datetime.now(UTC).replace(tzinfo=None)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(db: Session, account_id: int, profile_id: int | None = None) -> str:
    token = secrets.token_urlsafe(32)
    auth_session = AuthSession(
        id=_hash_token(token),
        account_id=account_id,
        profile_id=profile_id,
        expires_at=_utcnow() + SESSION_LIFETIME,
    )
    db.add(auth_session)
    db.commit()
    return token


def validate_session(db: Session, token: str) -> AuthSession | None:
    session = db.get(AuthSession, _hash_token(token))
    if session is None:
        return None

    if session.expires_at < _utcnow():
        delete_session(db, token)  # nettoyage paresseux
        return None  # ← le rejet, sans lui la session morte passerait

    # Cas nominal : session valide. Prolongation glissante si past mi-vie.
    if session.expires_at - _utcnow() < SESSION_LIFETIME / 2:
        session.expires_at = _utcnow() + SESSION_LIFETIME
        db.commit()

    return session


def delete_session(db: Session, token: str) -> None:
    session = db.get(AuthSession, _hash_token(token))
    if session:
        db.delete(session)
        db.commit()
