"""seed initial data

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text("INSERT INTO department (name) VALUES ('General')")
    )
    op.execute(
        sa.text("INSERT INTO role (name) VALUES ('admin'), ('user')")
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM role WHERE name IN ('admin', 'user')"))
    op.execute(sa.text("DELETE FROM department WHERE name = 'General'"))
