from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.identifiers import username_key
from app.core.security import hash_password, needs_rehash, verify_dummy, verify_password
from app.models.account import Account
from app.models.profile import Profile
from app.services.group_service import get_group_by_slug
from app.services.session_service import delete_account_session, delete_profile_sessions

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


class AccountServiceError(Exception):
    """Erreur métier de création/gestion de compte"""


class UsernameAlreadyExists(AccountServiceError): ...


class InvalidPassword(AccountServiceError): ...


class AccountNotFound(AccountServiceError): ...


class MultiProfileChangeForbidden(AccountServiceError): ...


class WrongPassword(AccountServiceError): ...


class PasswordChangeNotRequired(AccountServiceError): ...


class ProvisionalPasswordPending(AccountServiceError): ...


class InvalidProfileName(AccountServiceError): ...


class ProfileNameTaken(AccountServiceError): ...


class ProfileAlreadyDeactivated(AccountServiceError): ...


class ProfileNotDeactivated(AccountServiceError): ...


class SelfDeactivationForbidden(AccountServiceError): ...


class LastAdminForbidden(AccountServiceError): ...


def _account_by_username(db: Session, username: str) -> Account | None:
    """Recherche UNIQUE d'un compte par identifiant (insensible à la casse, via username_key)."""
    return db.scalar(select(Account).where(Account.username_key == username_key(username)))


def find_account(db: Session, username: str) -> Account:
    """Comme `_account_by_username`, mais lève AccountNotFound (CLI, reset, add_profile)."""
    account = _account_by_username(db, username)
    if account is None:
        raise AccountNotFound(f"Le compte '{username}' n'existe pas.")
    return account


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
    group_slug: str | None = None,
    display_name: str | None = None,
    is_admin: bool = False,
) -> Account:

    _validate_password_length(password)

    if _account_by_username(db, username) is not None:
        raise UsernameAlreadyExists(f"L'identifiant '{username}' est déjà pris.")

    # Sans groupe : utilisateur « lambda ». Validé AVANT tout calcul coûteux.
    group = get_group_by_slug(db, group_slug) if group_slug is not None else None

    password_hash = hash_password(password)

    account = Account(
        username=username,
        password_hash=password_hash,
        must_change_password=True,  # Forcer le changement de mot de passe à la première connexion
        is_admin=is_admin,
    )

    profile = Profile(display_name=display_name or username)
    if group is not None:
        profile.groups.append(group)
    account.profiles.append(profile)

    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def reset_password(db: Session, username: str, new_password: str) -> Account:
    _validate_password_length(new_password)

    account = find_account(db, username)

    account.password_hash = hash_password(new_password)
    # TOUS les profils, actifs ou non (D2, J5a) : un compte qui a été partagé le reste —
    # un profil désactivé connaît toujours la phrase de passe.
    account.must_change_password = len(account.profiles) == 1

    delete_account_session(db, account.id)
    db.commit()
    db.refresh(account)
    return account


def change_password(db: Session, account: Account, old_password: str, new_password: str) -> Account:
    if len(account.profiles) > 1:  # TOUS les profils (D2) — cf. reset_password
        raise MultiProfileChangeForbidden(
            "Le changement de mot de passe ne peut être effectué que par l'administrateur."
        )

    if not account.must_change_password:
        raise PasswordChangeNotRequired(
            "Aucun changement de mot de passe n'est attendu. Contactez l'administrateur."
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
    account = _account_by_username(db, username)
    if account is None:
        # Vérification factice pour éviter de révéler l'existence d'un identifiant
        # (anti-timing)
        verify_dummy(password)
        return None

    if not verify_password(password, account.password_hash):
        return None

    # Porte « login » (J5a) : compte sans profil actif → même refus qu'un mauvais mot
    # de passe (401 générique). Vérifié APRÈS le mot de passe : pas d'énumération par
    # le temps de réponse, et un tiers sans le mot de passe n'apprend rien.
    if not account.is_active:
        return None

    # Vérifier si le mot de passe doit être rehashé
    if needs_rehash(account.password_hash):
        account.password_hash = hash_password(password)
        db.commit()
        db.refresh(account)

    return account


def add_profile(
    db: Session, username: str, display_name: str, group_slug: str | None = None
) -> Profile:
    """Ajoute un profil à un compte existant (le rend multi-profils).

    INVARIANT préservé : must_change_password ⇒ mono-profil. Un compte encore en
    mot de passe provisoire est REFUSÉ : son titulaire doit d'abord poser son mot
    de passe définitif (sinon : changement interdit car multi-profils → impasse).
    """
    account = find_account(db, username)

    if account.must_change_password:
        raise ProvisionalPasswordPending(
            f"Le compte '{account.username}' a encore un mot de passe provisoire : "
            "il doit d'abord être changé à la connexion."
        )

    name = display_name.strip()
    if not name:
        raise InvalidProfileName("Le nom du profil ne peut pas être vide.")
    # TOUS les profils, désactivés compris : sinon une réactivation créerait un doublon.
    if any(p.display_name.casefold() == name.casefold() for p in account.profiles):
        raise ProfileNameTaken(f"Le compte '{account.username}' a déjà un profil « {name} ».")

    group = get_group_by_slug(db, group_slug) if group_slug is not None else None

    profile = Profile(display_name=name)
    if group is not None:
        profile.groups.append(group)
    account.profiles.append(profile)

    db.commit()
    db.refresh(profile)
    return profile


# --- Désactivation / réactivation (J5a) --------------------------------------------------
# Seuls les PROFILS portent un état (D1). Un compte est actif tant qu'il lui reste un
# profil actif : désactiver le dernier profil désactive le compte. Toutes ces opérations
# se terminent par UN SEUL commit (tout ou rien) : jamais de compte inactif avec des
# sessions encore valides, jamais de compte famille à moitié désactivé.


def _other_active_admin_exists(db: Session, account: Account) -> bool:
    return (
        db.scalar(
            select(Account.id).where(Account.is_admin, Account.is_active, Account.id != account.id)
        )
        is not None
    )


def _deactivate(
    db: Session, account: Account, targets: list[Profile], actor: Profile | None
) -> None:
    """Cœur commun à `deactivate_profile` et `deactivate_account`. Ne commite pas."""
    # Anti-verrouillage 1 : jamais soi-même. `actor` vaut None en CLI (pas de session).
    if actor is not None and any(p.id == actor.id for p in targets):
        raise SelfDeactivationForbidden("Vous ne pouvez pas désactiver votre propre profil.")

    target_ids = {p.id for p in targets}
    remaining_active = [p for p in account.active_profiles if p.id not in target_ids]

    # Anti-verrouillage 2 : jamais le dernier admin actif (s'applique AUSSI en CLI).
    if account.is_admin and not remaining_active and not _other_active_admin_exists(db, account):
        raise LastAdminForbidden("Impossible : c'est le dernier compte administrateur actif.")

    now = utcnow()
    for profile in targets:
        profile.deactivated_at = now

    if remaining_active:
        delete_profile_sessions(db, list(target_ids))  # D3 : les autres membres restent
    else:
        delete_account_session(db, account.id)  # dernier profil → compte inactif


def deactivate_profile(db: Session, profile: Profile, actor: Profile | None = None) -> Profile:
    """Désactive un profil (réversible). Ses recettes restent, intactes."""
    if not profile.is_active:
        raise ProfileAlreadyDeactivated(f"Le profil « {profile.display_name} » est déjà désactivé.")
    _deactivate(db, profile.account, [profile], actor)
    db.commit()
    db.refresh(profile)
    return profile


def deactivate_account(db: Session, account: Account, actor: Profile | None = None) -> Account:
    """Raccourci : désactive d'un coup tous les profils actifs du compte (même cœur)."""
    targets = account.active_profiles
    if not targets:
        raise ProfileAlreadyDeactivated(f"Le compte « {account.username} » est déjà inactif.")
    _deactivate(db, account, targets, actor)
    db.commit()
    db.refresh(account)
    return account


def reactivate_profile(db: Session, profile: Profile) -> Profile:
    """Réactive un profil — et donc son compte s'il était inactif (état dérivé)."""
    if profile.is_active:
        raise ProfileNotDeactivated(f"Le profil « {profile.display_name} » est déjà actif.")
    profile.deactivated_at = None
    db.commit()
    db.refresh(profile)
    return profile
