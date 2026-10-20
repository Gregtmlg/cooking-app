import pytest

from app.services.profile_service import (
    AmbiguousProfile,
    ProfileNotFound,
    find_profile,
    select_profile,
)


def test_select_profile_success(db_session, account, auth_session):
    profile = account.profiles[0]
    select_profile(db_session, auth_session, profile.id)
    assert auth_session.profile_id == profile.id


def test_unexisting_profile(db_session, auth_session):
    with pytest.raises(ProfileNotFound):
        select_profile(db_session, auth_session, 999)


def test_profile_not_belonging_to_account(db_session, auth_session, another_account):
    another_profile = another_account.profiles[0]
    with pytest.raises(ProfileNotFound):
        select_profile(db_session, auth_session, another_profile.id)


def test_find_profile_single_profile_without_name(db_session, account):

    assert find_profile(db_session, "Louise") is account.profiles[0]


def test_find_profile_multi_profile_without_name_is_ambiguous(db_session, multi_profile_account):

    with pytest.raises(AmbiguousProfile):
        find_profile(db_session, "Famille")


def test_find_profile_multi_profile_by_name(db_session, multi_profile_account):

    assert find_profile(db_session, "Famille", "Jeanne").display_name == "Jeanne"


def test_find_profile_unknown_account(db_session):

    with pytest.raises(ProfileNotFound):
        find_profile(db_session, "Inconnu")


def test_find_profile_unknown_name(db_session, account):

    with pytest.raises(ProfileNotFound):
        find_profile(db_session, "Louise", "Personne")
