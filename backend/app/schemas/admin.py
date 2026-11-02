from datetime import datetime

from pydantic import BaseModel


class ProfileEntryRead(BaseModel):
    id: int
    display_name: str
    groups: list[str]
    theme: str | None

    model_config = {"from_attributes": True}


class AccountEntryRead(BaseModel):
    id: int
    username: str
    is_admin: bool
    must_change_password: bool
    created_at: datetime
    active_sessions: int
    profiles: list[ProfileEntryRead]

    model_config = {"from_attributes": True}


class GroupEntryRead(BaseModel):
    slug: str
    name: str
    members: int

    model_config = {"from_attributes": True}


class InventoryRead(BaseModel):
    accounts: list[AccountEntryRead]
    groups: list[GroupEntryRead]

    model_config = {"from_attributes": True}


class AccountCreate(BaseModel):
    """Pas de champ `is_admin` : un admin ne se crée qu'en CLI, sur le serveur."""

    username: str
    password: str
    display_name: str | None = None
    group: str | None = None

    model_config = {"extra": "forbid"}


class PasswordReset(BaseModel):
    password: str

    model_config = {"extra": "forbid"}


class ProfileCreate(BaseModel):
    display_name: str
    group: str | None = None

    model_config = {"extra": "forbid"}


class OwnerChange(BaseModel):
    profile_id: int

    model_config = {"extra": "forbid"}


class OwnerRead(BaseModel):
    recipe_id: int
    owner_id: int
