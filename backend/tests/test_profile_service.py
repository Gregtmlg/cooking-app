import pytest

from app.services.profile_service import ProfileNotFound, select_profile


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
