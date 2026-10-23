"""set group themes and brands

Revision ID: f7829f748969
Revises: f5988978019a
Create Date: 2026-10-23 14:47:13.909170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7829f748969'
down_revision: Union[str, Sequence[str], None] = 'f5988978019a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Table GELÉE (même motif que le seed et le renommage) : jamais le modèle ORM.
groups_table = sa.table(
    "groups",
    sa.column("slug", sa.String),
    sa.column("theme", sa.String),
    sa.column("brand_name", sa.String),
)

VALUES = {
    "famille": {"theme": "famille", "brand_name": "Dingé Kitchen"},
    "chuteam": {"theme": "chuteam", "brand_name": "KitChuTeam"},
}


def upgrade() -> None:
    for slug, values in VALUES.items():
        op.execute(groups_table.update().where(groups_table.c.slug == slug).values(**values))


def downgrade() -> None:
    op.execute(
        groups_table.update()
        .where(groups_table.c.slug.in_(VALUES))
        .values(theme=None, brand_name=None)
    )