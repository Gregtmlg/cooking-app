import pytest
from sqlalchemy.exc import IntegrityError

from app.core.identifiers import username_key
from app.core.security import hash_password
from app.models.account import Account
from app.services.account_service import (
    UsernameAlreadyExists,
    authenticate,
    create_account,
)

NFC = "Ma\u00eblle"  # ë en un seul caractère
NFD = "Mae\u0308lle"  # e + tréma combinant : même rendu à l'écran


def test_username_key_folds_case_unicode_and_spaces():
    assert username_key("  ÉLODIE ") == "élodie"
    assert username_key(NFC) == username_key(NFD)


def test_accents_stay_distinct():
    assert username_key("Maëlle") != username_key("Maelle")


def test_username_stored_clean_with_case_kept(db_session):
    account = create_account(db_session, username="  Louise ", password="motdepasse123")
    assert account.username == "Louise"
    assert account.username_key == "louise"


def test_duplicate_differing_only_by_case_is_refused(db_session):
    create_account(db_session, username="Louise", password="motdepasse123")
    with pytest.raises(UsernameAlreadyExists):
        create_account(db_session, username="LOUISE", password="motdepasse123")


def test_unique_key_is_enforced_by_the_database(db_session):
    """Garantie STRUCTURELLE : même en contournant le service, la base refuse."""
    create_account(db_session, username="Louise", password="motdepasse123")
    db_session.add(Account(username="louise", password_hash=hash_password("motdepasse123")))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_key_follows_a_later_rename(db_session):
    account = create_account(db_session, username="Louise", password="motdepasse123")
    account.username = "Louisette"
    assert account.username_key == "louisette"


def test_authenticate_ignores_case_and_unicode_form(db_session):
    create_account(db_session, username=NFC, password="motdepasse123")
    assert authenticate(db_session, "maëlle", "motdepasse123") is not None
    assert authenticate(db_session, NFD, "motdepasse123") is not None
    assert authenticate(db_session, "Maelle", "motdepasse123") is None


def test_login_api_is_case_insensitive(client, account):
    response = client.post(
        "/api/v1/auth/login", json={"username": "  louise", "password": "motdepasse123"}
    )
    assert response.status_code == 200
    assert response.json()["account"]["username"] == "Louise"
