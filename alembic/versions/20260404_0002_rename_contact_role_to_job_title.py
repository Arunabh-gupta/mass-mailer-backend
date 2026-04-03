"""rename contact role to job_title

Revision ID: 20260404_0002
Revises: 20260330_0001
Create Date: 2026-04-04 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260404_0002"
down_revision: Union[str, Sequence[str], None] = "20260330_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("contacts", "role", new_column_name="job_title")


def downgrade() -> None:
    op.alter_column("contacts", "job_title", new_column_name="role")
