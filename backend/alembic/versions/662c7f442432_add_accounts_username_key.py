"""add accounts username_key

Revision ID: 662c7f442432
Revises: f7829f748969
Create Date: 2026-10-26 20:02:50.966394

"""
import unicodedata
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '662c7f442432'
down_revision: Union[str, Sequence[str], None] = 'f7829f748969'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _clean(raw: str) -> str:
    # Copie FIGÉE de app.core.identifiers : une migration ne doit pas dépendre
    # du code applicatif, qui évoluera après elle.
    return unicodedata.normalize("NFC", raw.strip())


def upgrade() -> None:
    """Ajoute username_key (unicité insensible à la casse), remplie depuis l'existant."""
    # 1. Calculer TOUTES les clés et détecter les collisions AVANT de toucher au schéma :
    #    sous SQLite, un échec après l'ajout de colonne laisserait la colonne en place.
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, username FROM accounts")).all()
    seen: dict[str, str] = {}
    updates = []
    for account_id, username in rows:
        cleaned = _clean(username)
        key = cleaned.casefold()
        if key in seen:
            raise RuntimeError(
                f"Collision d'identifiants : '{seen[key]}' et '{username}' donnent "
                f"la même clé '{key}'. Renommez l'un des deux comptes, puis relancez."
            )
        seen[key] = username
        updates.append({"id": account_id, "username": cleaned, "key": key})

    # 2. Colonne NULLABLE : une NOT NULL sans valeur casserait sur une table peuplée.
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("username_key", sa.String(length=100), nullable=True))

    # 3. Remplir (et nettoyer username au passage).
    for row in updates:
        conn.execute(
            sa.text("UPDATE accounts SET username = :username, username_key = :key WHERE id = :id"),
            row,
        )

    # 4. Seulement maintenant : NOT NULL + index unique NOMMÉ.
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.alter_column("username_key", existing_type=sa.String(length=100), nullable=False)
        batch_op.create_index("ix_accounts_username_key", ["username_key"], unique=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_index("ix_accounts_username_key")
        batch_op.drop_column('username_key')

    # ### end Alembic commands ###
