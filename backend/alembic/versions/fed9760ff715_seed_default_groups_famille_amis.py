"""seed default groups: famille, amis

Revision ID: fed9760ff715
Revises: d5b798225c48
Create Date: 2026-07-18 01:29:37.535581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fed9760ff715'
down_revision: Union[str, Sequence[str], None] = 'd5b798225c48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Représentation locale et GELÉE de la table — surtout pas le modèle ORM Group,
# qui pourrait évoluer et changer le comportement de rejeu de cette migration.
groups_table = sa.table(
    "groups",
    sa.column("name", sa.String),
    sa.column("slug", sa.String),
    sa.column("theme", sa.String),
)


def upgrade() -> None:
    op.bulk_insert(
        groups_table,
        [
            {"name": "Famille", "slug": "famille", "theme": None},
            {"name": "Amis", "slug": "amis", "theme": None},
        ],
    )


def downgrade() -> None:
    op.execute(
        groups_table.delete().where(groups_table.c.slug.in_(["famille", "amis"]))
    )