from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from app.api.deps import SESSION_COOKIE_NAME, CurrentAccount, DbSession
from app.core.config import settings
from app.core.rate_limit import rate_limit_login
from app.schemas.auth import AccountRead, LoginRequest
from app.services import account_service, session_service

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


@router.post("/login", response_model=AccountRead, dependencies=[Depends(rate_limit_login)])
def login(credentials: LoginRequest, db: DbSession, response: Response):
    account = account_service.authenticate(db, credentials.username, credentials.password)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect.",
        )

    token = session_service.create_session(db, account.id)
    _set_session_cookie(response, token)
    return account


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: DbSession,
    response: Response,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
):
    if session_token is not None:
        session_service.delete_session(db, session_token)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")


@router.get("/me", response_model=AccountRead)
def me(account: CurrentAccount):
    return account
