"""rename group amis to chuteam

Revision ID: 792c1c51f3e8
Revises: 8d94d2f7efa5
Create Date: 2026-10-19 19:22:24.760714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '792c1c51f3e8'
down_revision: Union[str, Sequence[str], None] = '8d94d2f7efa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

groups_table = sa.table(
    "groups",
    sa.column("name", sa.String),
    sa.column("slug", sa.String),
)

def upgrade() -> None:
    op.execute(
        groups_table.update()
        .where(groups_table.c.slug == "amis")
        .values(slug="chuteam", name="ChuTeam")
    )


def downgrade() -> None:
    op.execute(
        groups_table.update()
        .where(groups_table.c.slug == "chuteam")
        .values(slug="amis", name="Amis")
    )