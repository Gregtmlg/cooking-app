"""add system account

Revision ID: 913f054e527d
Revises: b368b33fbbd9
Create Date: 2026-11-25 21:12:13.122654

"""

from datetime import UTC, datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "913f054e527d"
down_revision: Union[str, Sequence[str], None] = "b368b33fbbd9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Valeurs FIGÉES (une migration ne dépend pas du code applicatif, qui évoluera après elle).
SYSTEM_USERNAME = "Système"
SYSTEM_USERNAME_KEY = "système"  # casefold(NFC(strip(...))), cf. app.core.identifiers
SYSTEM_DISPLAY_NAME = "Système"
# Hash INVALIDE (convention Unix « ! ») : Argon2 ne peut produire aucune chaîne qui
# lui corresponde ; verify_password, fail-closed, répond toujours « non ».
UNUSABLE_PASSWORD_HASH = "!"

accounts = sa.table(
    "accounts",
    sa.column("id", sa.Integer),
    sa.column("username", sa.String),
    sa.column("username_key", sa.String),
    sa.column("password_hash", sa.String),
    sa.column("must_change_password", sa.Boolean),
    sa.column("is_admin", sa.Boolean),
    sa.column("is_system", sa.Boolean),
    sa.column("created_at", sa.DateTime),
)
profiles = sa.table(
    "profiles",
    sa.column("id", sa.Integer),
    sa.column("account_id", sa.Integer),
    sa.column("display_name", sa.String),
    sa.column("deactivated_at", sa.DateTime),
)


def upgrade() -> None:
    """Compte « Système » (4c J5b) : SCHÉMA puis DONNÉES, dans la même révision.

    Les opérations s'exécutent dans l'ordre : une fois la colonne ajoutée, l'insertion
    peut l'utiliser (même principe que la migration username_key, J1).
    """
    # 1. Schéma : le drapeau, et l'index unique PARTIEL (un seul is_system = vrai).
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("is_system", sa.Boolean(), server_default=sa.false(), nullable=False)
        )
        batch_op.create_index(
            "uq_accounts_single_system",
            ["is_system"],
            unique=True,
            sqlite_where=sa.text("is_system = 1"),
            postgresql_where=sa.text("is_system"),
        )

    # 2. Données : le compte (non connectable, non admin, hors groupe) et son profil,
    #    DÉSACTIVÉ dès sa naissance → compte inactif par construction (porte du login).
    now = datetime.now(UTC).replace(tzinfo=None)
    conn = op.get_bind()
    account_id = conn.execute(
        accounts.insert()
        .values(
            username=SYSTEM_USERNAME,
            username_key=SYSTEM_USERNAME_KEY,
            password_hash=UNUSABLE_PASSWORD_HASH,
            must_change_password=False,
            is_admin=False,
            is_system=True,
            created_at=now,
        )
        .returning(accounts.c.id)
    ).scalar_one()
    conn.execute(
        profiles.insert().values(
            account_id=account_id, display_name=SYSTEM_DISPLAY_NAME, deactivated_at=now
        )
    )


def downgrade() -> None:
    """Refuse BRUYAMMENT si Système possède des recettes : une migration ne décide pas à
    qui les rendre (même philosophie que les collisions du J1). Les réattribuer d'abord."""
    conn = op.get_bind()
    system_profile_ids = [
        row[0]
        for row in conn.execute(
            sa.text(
                "SELECT p.id FROM profiles p JOIN accounts a ON a.id = p.account_id "
                "WHERE a.is_system = 1"
            )
        )
    ]
    if system_profile_ids:
        owned = conn.execute(
            sa.text("SELECT COUNT(*) FROM recipes WHERE owner_id IN :ids").bindparams(
                sa.bindparam("ids", expanding=True)
            ),
            {"ids": system_profile_ids},
        ).scalar_one()
        if owned:
            raise RuntimeError(
                f"Le compte Système possède {owned} recette(s) : réattribuez-les à un autre "
                "profil avant de revenir en arrière."
            )
        conn.execute(
            sa.text("DELETE FROM profiles WHERE id IN :ids").bindparams(
                sa.bindparam("ids", expanding=True)
            ),
            {"ids": system_profile_ids},
        )
        conn.execute(sa.text("DELETE FROM accounts WHERE is_system = 1"))

    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.drop_index("uq_accounts_single_system")
        batch_op.drop_column("is_system")
