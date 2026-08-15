import pytest

from app.core.security import verify_password
from app.services.account_service import (
    AccountNotFound,
    GroupNotFound,
    InvalidPassword,
    UsernameAlreadyExists,
    create_account,
    reset_password,
)


def test_create_account_nominal(db_session, amis_group):
    account = create_account(
        db_session, username="Louise", password="motdepasse123", group_slug="amis"
    )
    assert account.id is not None
    assert len(account.profiles) == 1
    assert account.profiles[0].groups[0].slug == "amis"


def test_password_is_hashed(db_session, amis_group):
    account = create_account(
        db_session, username="Louise", password="motdepasse123", group_slug="amis"
    )
    assert account.password_hash != "motdepasse123"
    assert verify_password("motdepasse123", account.password_hash) is True


def test_must_change_password_is_true(db_session, amis_group):
    account = create_account(
        db_session, username="Louise", password="motdepasse123", group_slug="amis"
    )
    assert account.must_change_password is True


def test_display_name_defaults_to_username(db_session, amis_group):
    account = create_account(
        db_session, username="Louise", password="motdepasse123", group_slug="amis"
    )
    assert account.profiles[0].display_name == "Louise"


def test_duplicate_username_raises(db_session, amis_group):
    create_account(db_session, username="Louise", password="motdepasse123", group_slug="amis")
    with pytest.raises(UsernameAlreadyExists):
        create_account(db_session, username="Louise", password="autremotdepasse", group_slug="amis")


def test_unknown_group_raises(db_session):
    with pytest.raises(GroupNotFound):
        create_account(
            db_session, username="Louise", password="motdepasse123", group_slug="inconnu"
        )


def test_password_too_short_raises(db_session, amis_group):
    with pytest.raises(InvalidPassword):
        create_account(db_session, username="Louise", password="short", group_slug="amis")


def test_reset_password_nominal(db_session, amis_group):
    account = create_account(
        db_session, username="Louise", password="motdepasse123", group_slug="amis"
    )
    old_hash = account.password_hash
    updated = reset_password(db_session, username="Louise", new_password="nouveaumotdepasse456")
    assert updated.password_hash != old_hash
    assert verify_password("nouveaumotdepasse456", updated.password_hash) is True
    assert updated.must_change_password is True


def test_reset_password_unknown_account_raises(db_session):
    with pytest.raises(AccountNotFound):
        reset_password(db_session, username="Inconnu", new_password="nouveaumotdepasse456")
