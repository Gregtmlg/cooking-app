from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from app.api.deps import (
    SESSION_COOKIE_NAME,
    CurrentAccount,
    CurrentProfile,
    CurrentSession,
    DbSession,
)
from app.core.config import settings
from app.core.rate_limit import rate_limit_login
from app.models.account import Account
from app.models.profile import Profile
from app.schemas.auth import (
    AccountRead,
    ChangePasswordRequest,
    LoginRequest,
    ProfileRead,
    SelectProfileRequest,
    SessionRead,
    ThemeChoice,
    ThemeRead,
)
from app.services import account_service, group_service, profile_service, session_service
from app.services.account_service import (
    InvalidPassword,
    MultiProfileChangeForbidden,
    PasswordChangeNotRequired,
    WrongPassword,
)
from app.services.group_service import GroupNotFound, NotInGroup
from app.services.profile_service import ProfileNotFound

router = APIRouter(prefix="/auth", tags=["auth"])

SESSION_MAX_AGE = 14 * 24 * 60 * 60  # 14 jours, en secondes — aligné sur SESSION_LIFETIME


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
        max_age=SESSION_MAX_AGE,
    )


def _session_read(account: Account, profile: Profile | None) -> SessionRead:
    """L'état complet de la session, thème compris (calculé par theme_for)."""
    if profile is None:
        return SessionRead(account=account, profile=None)
    theme = group_service.theme_for(profile)
    return SessionRead(
        account=account,
        profile=profile,
        theme=ThemeRead.from_group(theme) if theme else None,
        theme_options=[ThemeRead.from_group(g) for g in group_service.theme_options(profile)],
    )


@router.post("/login", response_model=SessionRead, dependencies=[Depends(rate_limit_login)])
def login(credentials: LoginRequest, db: DbSession, response: Response):
    account = account_service.authenticate(db, credentials.username, credentials.password)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect.",
        )
    # Auto-sélection si le compte n'a qu'un seul profil
    profile = account.profiles[0] if len(account.profiles) == 1 else None
    token = session_service.create_session(
        db, account.id, profile_id=profile.id if profile else None
    )
    _set_session_cookie(response, token)
    return _session_read(account, profile)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: DbSession,
    response: Response,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    if session_token is not None:
        session_service.delete_session(db, session_token)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")


@router.get("/me", response_model=SessionRead)
def me(auth_session: CurrentSession):
    return _session_read(auth_session.account, auth_session.profile)


@router.put("/theme", response_model=SessionRead)
def choose_theme(payload: ThemeChoice, profile: CurrentProfile, db: DbSession):
    """Choisit le thème du profil actif parmi ses groupes (None → défaut)."""
    try:
        group_service.set_theme(db, profile, payload.group)
    except NotInGroup as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from None
    except GroupNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)
        ) from None
    return _session_read(profile.account, profile)


@router.get("/profiles", response_model=list[ProfileRead])
def list_profiles(account: CurrentAccount):
    """Liste les profils du compte connecté (pour l'écran de sélection)."""
    return account.profiles


@router.post("/select-profile", response_model=ProfileRead)
def select_profile(
    payload: SelectProfileRequest,
    auth_session: CurrentSession,
    db: DbSession,
):
    """Sélectionne le profil actif de la session."""
    try:
        return profile_service.select_profile(db, auth_session, payload.profile_id)
    except ProfileNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from None


@router.post("/change-password", response_model=AccountRead)
def change_password(
    payload: ChangePasswordRequest,
    account: CurrentAccount,
    db: DbSession,
):
    try:
        return account_service.change_password(
            db, account, payload.old_password, payload.new_password
        )
    except (MultiProfileChangeForbidden, PasswordChangeNotRequired) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from None
    except (WrongPassword, InvalidPassword) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None
