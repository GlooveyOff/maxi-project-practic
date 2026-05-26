"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role = sa.Enum("guest", "employee", "admin", name="userrole")
field_status = sa.Enum("exploration", "active", "suspended", "depleted", name="fieldstatus")
well_status = sa.Enum("drilling", "operating", "maintenance", "closed", name="wellstatus")
request_status = sa.Enum("new", "in_progress", "done", "rejected", name="requeststatus")
request_priority = sa.Enum("low", "medium", "high", "critical", name="requestpriority")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="employee"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "fields",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False, unique=True),
        sa.Column("location", sa.String(length=200), nullable=False),
        sa.Column("reserves_tons", sa.Float(), nullable=False),
        sa.Column("discovered_year", sa.Integer(), nullable=False),
        sa.Column("status", field_status, nullable=False, server_default="exploration"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_fields_name", "fields", ["name"])

    op.create_table(
        "wells",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "field_id",
            sa.Integer(),
            sa.ForeignKey("fields.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("depth_m", sa.Float(), nullable=False),
        sa.Column("daily_output_tons", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", well_status, nullable=False, server_default="drilling"),
        sa.Column("drilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_wells_field_id", "wells", ["field_id"])

    op.create_table(
        "maintenance_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "well_id",
            sa.Integer(),
            sa.ForeignKey("wells.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "author_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", request_status, nullable=False, server_default="new"),
        sa.Column("priority", request_priority, nullable=False, server_default="medium"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_requests_well_id", "maintenance_requests", ["well_id"])
    op.create_index("ix_requests_author_id", "maintenance_requests", ["author_id"])


def downgrade() -> None:
    op.drop_table("maintenance_requests")
    op.drop_table("wells")
    op.drop_table("fields")
    op.drop_table("users")
    request_priority.drop(op.get_bind(), checkfirst=True)
    request_status.drop(op.get_bind(), checkfirst=True)
    well_status.drop(op.get_bind(), checkfirst=True)
    field_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
