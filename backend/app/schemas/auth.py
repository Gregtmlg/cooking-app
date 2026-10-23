from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.models.group import Group


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


class ThemeRead(BaseModel):
    slug: str  # le groupe (pour le choix)
    key: str | None  # clé CSS : [data-theme="…"] ; None → palette neutre
    brand: str | None  # libellé de marque ; None → libellé neutre (front)

    @classmethod
    def from_group(cls, group: "Group") -> "ThemeRead":
        return cls(slug=group.slug, key=group.theme, brand=group.brand_name)


class ThemeChoice(BaseModel):
    group: str | None  # slug du groupe choisi ; None → revenir au défaut


class SessionRead(BaseModel):
    account: AccountRead
    profile: ProfileRead | None = None
    theme: ThemeRead | None = None  # thème actif, décidé par theme_for (None = neutre)
    theme_options: list[ThemeRead] = []  # ≥ 2 → le front affiche le sélecteur

    model_config = {"from_attributes": True}
