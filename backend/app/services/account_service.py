from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, needs_rehash, verify_dummy, verify_password
from app.models.account import Account
from app.models.group import Group
from app.models.profile import Profile

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


class AccountServiceError(Exception):
    """Erreur métier de création/gestion de compte"""


class UsernameAlreadyExists(AccountServiceError): ...


class GroupNotFound(AccountServiceError): ...


class InvalidPassword(AccountServiceError): ...


class AccountNotFound(AccountServiceError): ...


class MultiProfileChangeForbidden(AccountServiceError): ...


class WrongPassword(AccountServiceError): ...


def _validate_password_length(password: str) -> None:
    if not (MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH):
        raise InvalidPassword(
            f"Le mot de passe doit contenir entre {MIN_PASSWORD_LENGTH} "
            f"et {MAX_PASSWORD_LENGTH} caractères."
        )


def create_account(
    db: Session,
    username: str,
    password: str,
    group_slug: str,
    display_name: str | None = None,
    is_admin: bool = False,
) -> Account:

    _validate_password_length(password)

    if db.scalar(select(Account).where(Account.username == username)) is not None:
        raise UsernameAlreadyExists(f"L'identifiant '{username}' est déjà pris.")

    group = db.scalar(select(Group).where(Group.slug == group_slug))
    if group is None:
        raise GroupNotFound(f"Le groupe '{group_slug}' n'existe pas.")

    password_hash = hash_password(password)

    account = Account(
        username=username,
        password_hash=password_hash,
        must_change_password=True,  # Forcer le changement de mot de passe à la première connexion
        is_admin=is_admin,
    )

    profile = Profile(display_name=display_name or username)
    profile.groups.append(group)
    account.profiles.append(profile)

    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def reset_password(db: Session, username: str, new_password: str) -> Account:
    _validate_password_length(new_password)

    account = db.scalar(select(Account).where(Account.username == username))
    if account is None:
        raise AccountNotFound(f"Le compte '{username}' n'existe pas.")

    account.password_hash = hash_password(new_password)
    account.must_change_password = (
        len(account.profiles) == 1
    )  # Forcer le changement de mot de passe si le compte n'a qu'un profil

    db.commit()
    db.refresh(account)
    return account


def change_password(db: Session, account: Account, old_password: str, new_password: str) -> Account:
    if len(account.profiles) > 1:
        raise MultiProfileChangeForbidden(
            "Le changement de mot de passe ne peut être effectué que par l'administrateur."
        )

    _validate_password_length(new_password)
    if not verify_password(old_password, account.password_hash):
        raise WrongPassword("Ancien mot de passe incorrect.")

    account.password_hash = hash_password(new_password)
    account.must_change_password = False  # Le mot de passe a été changé avec succès
    db.commit()
    db.refresh(account)
    return account


def authenticate(db: Session, username: str, password: str) -> Account | None:
    account = db.scalar(select(Account).where(Account.username == username))
    if account is None:
        # Vérification factice pour éviter de révéler l'existence d'un identifiant
        # (anti-timing)
        verify_dummy(password)
        return None

    if not verify_password(password, account.password_hash):
        return None

    # Vérifier si le mot de passe doit être rehashé
    if needs_rehash(account.password_hash):
        account.password_hash = hash_password(password)
        db.commit()
        db.refresh(account)

    return account
