from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AccountRead(BaseModel):
    username: str
    must_change_password: bool
    is_admin: bool

    model_config = {"from_attributes": True}


class ProfileRead(BaseModel):
    id: int
    display_name: str
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class SelectProfileRequest(BaseModel):
    profile_id: int


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class SessionRead(BaseModel):
    account: AccountRead
    profile: ProfileRead | None = None

    model_config = {"from_attributes": True}
