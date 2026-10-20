import pytest

from app.models.group import Group
from app.services.group_service import (
    AlreadyInGroup,
    GroupNotFound,
    NotInGroup,
    add_profile_to_group,
    get_group_by_slug,
    remove_profile_from_group,
)


@pytest.fixture
def famille_group(db_session):
    group = Group(slug="famille", name="Famille")
    db_session.add(group)
    db_session.commit()
    return group


def test_get_group_by_slug_unknown_raises(db_session):
    with pytest.raises(GroupNotFound):
        get_group_by_slug(db_session, "inconnu")


def test_add_profile_to_group(db_session, account, famille_group):
    profile = account.profiles[0]  # déjà dans chuteam
    add_profile_to_group(db_session, profile, "famille")
    assert {g.slug for g in profile.groups} == {"chuteam", "famille"}


def test_add_profile_already_in_group_raises(db_session, account):
    with pytest.raises(AlreadyInGroup):
        add_profile_to_group(db_session, account.profiles[0], "chuteam")


def test_remove_last_group_leaves_profile_without_group(db_session, account):
    profile = account.profiles[0]
    remove_profile_from_group(db_session, profile, "chuteam")
    assert profile.groups == []


def test_remove_profile_not_in_group_raises(db_session, account, famille_group):
    with pytest.raises(NotInGroup):
        remove_profile_from_group(db_session, account.profiles[0], "famille")
