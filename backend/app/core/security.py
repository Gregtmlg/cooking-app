from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# On se base sur les recommendations de l'OWASP pour le stockage des mots de passe :
# https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
# ~ 19 MiB/hash


_password_hasher = PasswordHasher(
    memory_cost=19456,  # en KiB, soit 19 MiB
    time_cost=2,  # nombre d'itérations
    parallelism=1,  # nombre de threads
)

# Hash factice (anti-timing), empêche de révéler l'existence d'un identifiant
_DUMMY_HASH = _password_hasher.hash("dummy_password_for_timing")


def needs_rehash(hashed: str) -> bool:
    """Check if a password hash needs to be rehashed."""
    return _password_hasher.check_needs_rehash(hashed)


def verify_dummy(plain: str) -> None:
    """Verify a password against a dummy hash to prevent timing attacks."""
    try:
        _password_hasher.verify(_DUMMY_HASH, plain)
    except (InvalidHashError, VerifyMismatchError):
        pass  # On ne fait rien, c'est juste pour le timing


def hash_password(plain: str) -> str:
    """Hash a password using Argon2."""
    return _password_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a hash using Argon2."""
    try:
        _password_hasher.verify(hashed, plain)
        return True
    except (InvalidHashError, VerifyMismatchError):
        return False
