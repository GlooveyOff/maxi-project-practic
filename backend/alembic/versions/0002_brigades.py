"""brigades + brigade_id/closed_at в заявках

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-28
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


brigade_status = sa.Enum(
    "available", "on_site", "resting", "off_duty", name="brigadestatus"
)


def upgrade() -> None:
    op.create_table(
        "brigades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("foreman", sa.String(length=150), nullable=False),
        sa.Column("members_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("status", brigade_status, nullable=False, server_default="available"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_brigades_name", "brigades", ["name"])

    op.add_column(
        "maintenance_requests",
        sa.Column(
            "brigade_id",
            sa.Integer(),
            sa.ForeignKey("brigades.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "maintenance_requests",
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_requests_brigade_id", "maintenance_requests", ["brigade_id"])


def downgrade() -> None:
    op.drop_index("ix_requests_brigade_id", table_name="maintenance_requests")
    op.drop_column("maintenance_requests", "closed_at")
    op.drop_column("maintenance_requests", "brigade_id")

    op.drop_index("ix_brigades_name", table_name="brigades")
    op.drop_table("brigades")
    brigade_status.drop(op.get_bind(), checkfirst=True)
