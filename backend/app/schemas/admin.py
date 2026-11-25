from datetime import datetime

from pydantic import BaseModel


class ProfileEntryRead(BaseModel):
    id: int
    display_name: str
    groups: list[str]
    theme: str | None
    deactivated_at: datetime | None

    model_config = {"from_attributes": True}


class AccountEntryRead(BaseModel):
    id: int
    username: str
    is_admin: bool
    must_change_password: bool
    is_active: bool
    is_system: bool
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


class PurgeConfirm(BaseModel):
    """Confirmation vérifiée PAR LE SERVEUR : le nom (profil) ou l'identifiant (compte),
    retapé exactement. Une confirmation qui n'existerait que dans le front serait
    contournée par Swagger, curl ou la CLI (principe 8)."""

    confirm: str

    model_config = {"extra": "forbid"}


class PurgeRead(BaseModel):
    """Résultat d'une purge : des ids seulement, aucun nom."""

    account_id: int
    profile_ids: list[int]
    account_deleted: bool
    recipes_reassigned: int

    model_config = {"from_attributes": True}
