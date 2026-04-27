"""add campaign contact delivery tracking

Revision ID: 20260428_0003
Revises: 20260404_0002
Create Date: 2026-04-28 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260428_0003"
down_revision: Union[str, Sequence[str], None] = "20260404_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = _column_names(inspector, "campaign_contacts")

    if "processed_at" not in existing_columns:
        op.add_column("campaign_contacts", sa.Column("processed_at", sa.DateTime(), nullable=True))
    if "provider_message_id" not in existing_columns:
        op.add_column(
            "campaign_contacts",
            sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("campaign_contacts", "provider_message_id")
    op.drop_column("campaign_contacts", "processed_at")
