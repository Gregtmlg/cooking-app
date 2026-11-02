import pytest

from app.services.account_service import (
    AccountNotFound,
    InvalidProfileName,
    ProfileNameTaken,
    ProvisionalPasswordPending,
    add_profile,
    create_account,
)
from app.services.group_service import GroupNotFound


@pytest.fixture
def settled_account(db_session, chuteam_group):
    """Compte mono-profil dont le mot de passe est déjà définitif."""
    account = create_account(
        db_session, username="Louise", password="motdepasse123", group_slug="chuteam"
    )
    account.must_change_password = False
    db_session.commit()
    return account


def test_add_profile_nominal(db_session, settled_account):
    profile = add_profile(db_session, "Louise", "Paul", group_slug="chuteam")
    assert profile.account_id == settled_account.id
    assert [g.slug for g in profile.groups] == ["chuteam"]
    assert len(settled_account.profiles) == 2


def test_add_profile_without_group(db_session, settled_account):
    assert add_profile(db_session, "Louise", "Paul").groups == []


def test_add_profile_refused_while_password_provisional(db_session, account):
    # `account` sort de create_account : must_change_password = True
    with pytest.raises(ProvisionalPasswordPending):
        add_profile(db_session, "Louise", "Paul")
    assert len(account.profiles) == 1  # rien n'a été créé


def test_invariant_holds_after_add_profile(db_session, settled_account):
    add_profile(db_session, "Louise", "Paul")
    assert not (settled_account.must_change_password and len(settled_account.profiles) > 1)


def test_add_profile_finds_account_case_insensitively(db_session, settled_account):
    assert add_profile(db_session, "  louise ", "Paul").account_id == settled_account.id


def test_add_profile_unknown_account(db_session):
    with pytest.raises(AccountNotFound):
        add_profile(db_session, "Personne", "Paul")


@pytest.mark.parametrize("name", ["", "   "])
def test_add_profile_empty_name(db_session, settled_account, name):
    with pytest.raises(InvalidProfileName):
        add_profile(db_session, "Louise", name)


def test_add_profile_duplicate_name_in_same_account(db_session, settled_account):
    with pytest.raises(ProfileNameTaken):
        add_profile(db_session, "Louise", "  LOUISE ")


def test_add_profile_unknown_group(db_session, settled_account):
    with pytest.raises(GroupNotFound):
        add_profile(db_session, "Louise", "Paul", group_slug="inconnu")
    assert len(settled_account.profiles) == 1


def test_reset_after_add_profile_keeps_password_definitive(db_session, settled_account):
    """Bout en bout de l'invariant : devenu multi-profils, un reset ne force plus rien."""
    from app.services.account_service import reset_password

    add_profile(db_session, "Louise", "Paul")
    assert reset_password(db_session, "Louise", "phrasedepasse").must_change_password is False
