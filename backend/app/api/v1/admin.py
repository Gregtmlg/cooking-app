"""Back-office admin. TOUTES les routes héritent de `require_admin` (niveau routeur).

Chaque action d'écriture : retrouve les objets par id → appelle le SERVICE (le même
que la CLI) → journalise un événement `admin.*` signé par l'admin (`actor_*`).
"""

import logging
from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import AdminAccount, CurrentProfile, DbSession, require_admin
from app.models.account import Account
from app.models.profile import Profile
from app.schemas.admin import (
    AccountCreate,
    AccountEntryRead,
    InventoryRead,
    OwnerChange,
    OwnerRead,
    PasswordReset,
    ProfileCreate,
    ProfileEntryRead,
)
from app.services import account_service, group_service, recipe_service
from app.services.account_service import (
    AccountNotFound,
    AccountServiceError,
    InvalidPassword,
    InvalidProfileName,
    ProfileNameTaken,
    ProvisionalPasswordPending,
    UsernameAlreadyExists,
)
from app.services.group_service import AlreadyInGroup, GroupNotFound, GroupServiceError, NotInGroup
from app.services.inventory_service import account_entry, get_inventory, profile_entry
from app.services.recipe_service import NewOwnerNotFound, RecipeServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# TABLE UNIQUE de traduction erreur métier → code HTTP
_HTTP_STATUS: dict[type[Exception], int] = {
    AccountNotFound: status.HTTP_404_NOT_FOUND,
    UsernameAlreadyExists: status.HTTP_409_CONFLICT,
    ProfileNameTaken: status.HTTP_409_CONFLICT,
    ProvisionalPasswordPending: status.HTTP_409_CONFLICT,
    AlreadyInGroup: status.HTTP_409_CONFLICT,
    NotInGroup: status.HTTP_409_CONFLICT,
    InvalidPassword: status.HTTP_422_UNPROCESSABLE_CONTENT,
    InvalidProfileName: status.HTTP_422_UNPROCESSABLE_CONTENT,
    GroupNotFound: status.HTTP_422_UNPROCESSABLE_CONTENT,  # groupe nommé dans le CORPS
    NewOwnerNotFound: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


_DOMAIN_ERRORS = (AccountServiceError, GroupServiceError, RecipeServiceError)


def _http_error(error: Exception) -> HTTPException:
    """Erreur métier → HTTPException. Une erreur absente de la table est RE-LEVÉE (→ 500) :
    un oubli se voit au lieu d'être maquillé en code arbitraire."""
    for error_type, code in _HTTP_STATUS.items():
        if isinstance(error, error_type):
            return HTTPException(status_code=code, detail=str(error))
    raise error


def _actor(admin: Account) -> dict[str, object]:
    """Signature de l'auteur, commune aux succès et aux refus."""
    return {"actor_account_id": admin.id, "actor_username": admin.username}


def _audit(event: str, admin: Account, **fields) -> None:
    """Journal d'audit d'une action RÉUSSIE. JAMAIS de mot de passe ici."""
    logger.info(event, extra={**_actor(admin), **fields})


@contextmanager
def _audited(action: str, admin: Account, **fields) -> Iterator[None]:
    """Journalise toute HTTPException levée dans le bloc (= action refusée), puis la relance.

    Un seul point couvre tous les refus d'une route : 404 des `_or_404`, erreurs métier
    traduites par `_http_error`, 404 explicites. Les cibles passées sont celles DEMANDÉES
    (URL / corps) : en cas de refus, l'objet n'existe peut-être pas.
    Hors champ : les 422 de Pydantic (avant la route, visibles dans le journal d'accès
    d'uvicorn) et les erreurs 500 (bugs, pas des refus : traceback dans uvicorn.error).
    """
    try:
        yield
    except HTTPException as e:
        logger.warning(
            "admin.action_refused",
            extra={
                **_actor(admin),
                "action": action,
                "status": e.status_code,
                "reason": e.detail,
                **fields,
            },
        )
        raise


def _account_or_404(db: Session, account_id: int) -> Account:
    account = db.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte introuvable.")
    return account


def _profile_or_404(db: Session, profile_id: int) -> Profile:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil introuvable.")
    return profile


@router.get("/inventory", response_model=InventoryRead)
def read_inventory(db: DbSession):
    return get_inventory(db)


@router.post("/accounts", response_model=AccountEntryRead, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, db: DbSession, admin: AdminAccount):
    with _audited("account_created", admin, target_username=payload.username):
        try:
            account = account_service.create_account(
                db,
                username=payload.username,
                password=payload.password,
                group_slug=payload.group,
                display_name=payload.display_name,
            )
        except _DOMAIN_ERRORS as e:
            raise _http_error(e) from None
        _audit(
            "admin.account_created",
            admin,
            target_account_id=account.id,
            target_username=account.username,
            group=payload.group,
        )
        return account_entry(account)


@router.post("/accounts/{account_id}/reset-password", response_model=AccountEntryRead)
def reset_password(account_id: int, payload: PasswordReset, db: DbSession, admin: AdminAccount):
    with _audited("password_reset", admin, target_account_id=account_id):
        account = _account_or_404(db, account_id)
        try:
            account = account_service.reset_password(db, account.username, payload.password)
        except _DOMAIN_ERRORS as e:
            raise _http_error(e) from None
        _audit(
            "admin.password_reset",
            admin,
            target_account_id=account.id,
            target_username=account.username,
        )
        return account_entry(account)


@router.post(
    "/accounts/{account_id}/profiles",
    response_model=ProfileEntryRead,
    status_code=status.HTTP_201_CREATED,
)
def add_profile(account_id: int, payload: ProfileCreate, db: DbSession, admin: AdminAccount):
    with _audited("profile_added", admin, target_account_id=account_id):
        account = _account_or_404(db, account_id)
        try:
            profile = account_service.add_profile(
                db, account.username, payload.display_name, group_slug=payload.group
            )
        except _DOMAIN_ERRORS as e:
            raise _http_error(e) from None
        _audit(
            "admin.profile_added",
            admin,
            target_account_id=account.id,
            target_profile_id=profile.id,
            group=payload.group,
        )
        return profile_entry(profile)


@router.put("/profiles/{profile_id}/groups/{slug}", response_model=ProfileEntryRead)
def add_to_group(profile_id: int, slug: str, db: DbSession, admin: AdminAccount):
    with _audited("group_member_added", admin, target_profile_id=profile_id, group=slug):
        profile = _profile_or_404(db, profile_id)
        try:
            group_service.add_profile_to_group(db, profile, slug)
        except GroupNotFound as e:  # groupe nommé dans l'URL : ressource introuvable
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
        except _DOMAIN_ERRORS as e:
            raise _http_error(e) from None
        _audit("admin.group_member_added", admin, target_profile_id=profile.id, group=slug)
        return profile_entry(profile)


@router.delete("/profiles/{profile_id}/groups/{slug}", response_model=ProfileEntryRead)
def remove_from_group(profile_id: int, slug: str, db: DbSession, admin: AdminAccount):
    with _audited("group_member_removed", admin, target_profile_id=profile_id, group=slug):
        profile = _profile_or_404(db, profile_id)
        try:
            group_service.remove_profile_from_group(db, profile, slug)
        except GroupNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from None
        except _DOMAIN_ERRORS as e:
            raise _http_error(e) from None
        _audit("admin.group_member_removed", admin, target_profile_id=profile.id, group=slug)
        return profile_entry(profile)


@router.put("/recipes/{recipe_id}/owner", response_model=OwnerRead)
def reassign_recipe(
    recipe_id: int, payload: OwnerChange, db: DbSession, admin: AdminAccount, actor: CurrentProfile
):
    with _audited("recipe_reassigned", admin, recipe_id=recipe_id):
        previous = recipe_service.get_recipe(db, actor, recipe_id)
        previous_owner_id = previous.owner_id if previous else None
        try:
            recipe = recipe_service.reassign_recipe(db, actor, recipe_id, payload.profile_id)
        except _DOMAIN_ERRORS as e:
            raise _http_error(e) from None
        if recipe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Recette introuvable."
            )
        _audit(
            "admin.recipe_reassigned",
            admin,
            recipe_id=recipe.id,
            previous_owner_id=previous_owner_id,
            new_owner_id=recipe.owner_id,
        )
        return OwnerRead(recipe_id=recipe.id, owner_id=recipe.owner_id)  # type: ignore
