from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from app.api.deps import SESSION_COOKIE_NAME, CurrentAccount, CurrentSession, DbSession
from app.core.config import settings
from app.core.rate_limit import rate_limit_login
from app.schemas.auth import (
    AccountRead,
    ChangePasswordRequest,
    LoginRequest,
    ProfileRead,
    SelectProfileRequest,
    SessionRead,
)
from app.services import account_service, profile_service, session_service
from app.services.account_service import (
    InvalidPassword,
    MultiProfileChangeForbidden,
    WrongPassword,
)
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
    return {"account": account, "profile": profile}


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
    return auth_session


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
    except MultiProfileChangeForbidden as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from None
    except (WrongPassword, InvalidPassword) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from None
