import unicodedata


def clean_username(raw: str) -> str:
    """Espaces de bord retirés + forme Unicode canonique (NFC). Casse conservée."""
    return unicodedata.normalize("NFC", raw.strip())


def username_key(raw: str) -> str:
    """Clé de comparaison : identifiant nettoyé, puis replié en casse (Unicode complet)."""
    return clean_username(raw).casefold()
