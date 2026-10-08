import pytest
from fastapi import HTTPException

from app.api.deps import (
    PASSWORD_CHANGE_REQUIRED,
    PROFILE_REQUIRED,
    get_current_profile,
    require_password_changed,
)


def test_profile_required_code(auth_session):
    with pytest.raises(HTTPException) as exc_info:
        get_current_profile(auth_session)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == PROFILE_REQUIRED


def test_password_change_required_code(account):
    with pytest.raises(HTTPException) as exc_info:
        require_password_changed(account)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == PASSWORD_CHANGE_REQUIRED
