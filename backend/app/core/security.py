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
