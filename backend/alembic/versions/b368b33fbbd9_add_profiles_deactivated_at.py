"""add profiles deactivated_at

Revision ID: b368b33fbbd9
Revises: 662c7f442432
Create Date: 2026-11-11 19:23:07.444539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b368b33fbbd9'
down_revision: Union[str, Sequence[str], None] = '662c7f442432'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Désactivation des profils (4c J5a) : une colonne NULLABLE, purement additive.

    NULL = profil actif. Les profils existants reçoivent NULL : ils sont donc tous actifs,
    sans migration de données. Le compte, lui, n'a pas d'état stocké (dérivé des profils).
    """
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('deactivated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Retire la colonne (perd les dates de désactivation : tout redevient actif)."""
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.drop_column('deactivated_at')
