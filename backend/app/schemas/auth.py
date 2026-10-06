from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AccountRead(BaseModel):
    username: str
    must_change_password: bool
    is_admin: bool

    model_config = {"from_attributes": True}
