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


def _column_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _index_map(inspector: sa.Inspector, table_name: str) -> dict[str, dict]:
    return {index["name"]: index for index in inspector.get_indexes(table_name)}


def _foreign_key_names(inspector: sa.Inspector, table_name: str) -> set[str]:
    return {
        foreign_key["name"]
        for foreign_key in inspector.get_foreign_keys(table_name)
        if foreign_key.get("name")
    }


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    contacts_columns = _column_names(inspector, "contacts")
    template_columns = _column_names(inspector, "email_template")
    campaign_columns = _column_names(inspector, "campaigns")

    if "user_id" not in contacts_columns:
        op.add_column("contacts", sa.Column("user_id", sa.UUID(), nullable=True))
    if "user_id" not in template_columns:
        op.add_column("email_template", sa.Column("user_id", sa.UUID(), nullable=True))
    if "user_id" not in campaign_columns:
        op.add_column("campaigns", sa.Column("user_id", sa.UUID(), nullable=True))

    inspector = sa.inspect(bind)
    contacts_foreign_keys = _foreign_key_names(inspector, "contacts")
    template_foreign_keys = _foreign_key_names(inspector, "email_template")
    campaign_foreign_keys = _foreign_key_names(inspector, "campaigns")

    if "fk_contacts_user_id_users" not in contacts_foreign_keys:
        op.create_foreign_key(
            "fk_contacts_user_id_users",
            "contacts",
            "users",
            ["user_id"],
            ["id"],
        )
    if "fk_email_template_user_id_users" not in template_foreign_keys:
        op.create_foreign_key(
            "fk_email_template_user_id_users",
            "email_template",
            "users",
            ["user_id"],
            ["id"],
        )
    if "fk_campaigns_user_id_users" not in campaign_foreign_keys:
        op.create_foreign_key(
            "fk_campaigns_user_id_users",
            "campaigns",
            "users",
            ["user_id"],
            ["id"],
        )

    inspector = sa.inspect(bind)
    contact_indexes = _index_map(inspector, "contacts")
    template_indexes = _index_map(inspector, "email_template")
    campaign_indexes = _index_map(inspector, "campaigns")

    existing_unique_constraints = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("contacts")
        if constraint.get("name")
    }

    if "contacts_email_key" in existing_unique_constraints:
        op.drop_constraint("contacts_email_key", "contacts", type_="unique")

    if contact_indexes.get("ix_contacts_email", {}).get("unique"):
        op.drop_index("ix_contacts_email", table_name="contacts")

    if "ix_contacts_user_id" not in contact_indexes:
        op.create_index("ix_contacts_user_id", "contacts", ["user_id"], unique=False)
    if "ix_email_template_user_id" not in template_indexes:
        op.create_index("ix_email_template_user_id", "email_template", ["user_id"], unique=False)
    if "ix_campaigns_user_id" not in campaign_indexes:
        op.create_index("ix_campaigns_user_id", "campaigns", ["user_id"], unique=False)
    if "uq_contacts_user_id_email" not in contact_indexes:
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
