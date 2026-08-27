# tests/test_session_service.py
from datetime import timedelta

import pytest

from app.models.session import AuthSession
from app.services.account_service import create_account
from app.services.session_service import (
    _hash_token,
    _utcnow,
    create_session,
    delete_session,
    validate_session,
)


@pytest.fixture
def account(db_session, amis_group):
    return create_account(
        db_session, username="louise", password="motdepasse123", group_slug="amis"
    )


def test_create_returns_clear_token_not_stored(db_session, account):
    token = create_session(db_session, account.id)
    # le jeton clair n'est PAS ce qui est stocké (la base a le condensat)
    assert db_session.get(AuthSession, token) is None  # le clair n'est pas une PK
    assert db_session.get(AuthSession, _hash_token(token)) is not None  # le condensat, si


def test_validate_ok(db_session, account):
    token = create_session(db_session, account.id)
    session = validate_session(db_session, token)
    assert session is not None
    assert session.account_id == account.id


def test_validate_bad_token(db_session):
    session = validate_session(db_session, "jeton-inexistant")
    assert session is None


def test_delete_then_validate(db_session, account):
    token = create_session(db_session, account.id)
    delete_session(db_session, token)
    session = validate_session(db_session, token)
    assert session is None


def test_validate_expired(db_session, account):

    token = create_session(db_session, account.id)
    # on force l'expiration en arrière
    session = db_session.get(AuthSession, _hash_token(token))
    session.expires_at = _utcnow() - timedelta(seconds=1)
    db_session.commit()

    # la validation échoue et supprime la session expirée
    assert validate_session(db_session, token) is None
    assert db_session.get(AuthSession, _hash_token(token)) is None
