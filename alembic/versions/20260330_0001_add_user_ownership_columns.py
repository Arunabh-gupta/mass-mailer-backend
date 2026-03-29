"""add user ownership columns

Revision ID: 20260330_0001
Revises: 
Create Date: 2026-03-30 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260330_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("contacts", sa.Column("user_id", sa.UUID(), nullable=True))
    op.add_column("email_template", sa.Column("user_id", sa.UUID(), nullable=True))
    op.add_column("campaigns", sa.Column("user_id", sa.UUID(), nullable=True))

    op.create_foreign_key(
        "fk_contacts_user_id_users",
        "contacts",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_email_template_user_id_users",
        "email_template",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_campaigns_user_id_users",
        "campaigns",
        "users",
        ["user_id"],
        ["id"],
    )

    op.drop_constraint("contacts_email_key", "contacts", type_="unique")
    op.create_index("ix_contacts_user_id", "contacts", ["user_id"], unique=False)
    op.create_index("ix_email_template_user_id", "email_template", ["user_id"], unique=False)
    op.create_index("ix_campaigns_user_id", "campaigns", ["user_id"], unique=False)
    op.create_index(
        "uq_contacts_user_id_email",
        "contacts",
        ["user_id", "email"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_contacts_user_id_email", table_name="contacts")
    op.drop_index("ix_campaigns_user_id", table_name="campaigns")
    op.drop_index("ix_email_template_user_id", table_name="email_template")
    op.drop_index("ix_contacts_user_id", table_name="contacts")

    op.create_unique_constraint("contacts_email_key", "contacts", ["email"])

    op.drop_constraint("fk_campaigns_user_id_users", "campaigns", type_="foreignkey")
    op.drop_constraint("fk_email_template_user_id_users", "email_template", type_="foreignkey")
    op.drop_constraint("fk_contacts_user_id_users", "contacts", type_="foreignkey")

    op.drop_column("campaigns", "user_id")
    op.drop_column("email_template", "user_id")
    op.drop_column("contacts", "user_id")
