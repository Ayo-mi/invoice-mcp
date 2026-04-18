"""initial invoice and vendor tables

Revision ID: 20260418_0001
Revises:
Create Date: 2026-04-18
"""

from collections.abc import Sequence
from typing import Optional, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260418_0001"
down_revision: Optional[str] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("invoice_id", sa.String(length=128), nullable=True),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("vendor", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=16), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("raw_text", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invoices_user_invoice_id", "invoices", ["user_id", "invoice_id"], unique=False)
    op.create_index("ix_invoices_user_vendor_date", "invoices", ["user_id", "vendor", "date"], unique=False)

    op.create_table(
        "vendors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("avg_amount", sa.Float(), nullable=False),
        sa.Column("invoice_count", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_vendors_user_name"),
    )
    op.create_index("ix_vendors_user_name", "vendors", ["user_id", "name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_vendors_user_name", table_name="vendors")
    op.drop_table("vendors")
    op.drop_index("ix_invoices_user_vendor_date", table_name="invoices")
    op.drop_index("ix_invoices_user_invoice_id", table_name="invoices")
    op.drop_table("invoices")

