"""Add due_date column to tasks table.

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000
"""
from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("due_date", sa.Date(), nullable=True),
    )
    op.execute(f"UPDATE tasks SET due_date = '{date.today().isoformat()}' WHERE due_date IS NULL")
    op.alter_column("tasks", "due_date", nullable=False)


def downgrade() -> None:
    op.drop_column("tasks", "due_date")
