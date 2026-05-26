"""Baseline schema.

Captures the schema as it exists at the end of Stage 6 (cameras, recordings,
users). Existing databases that already had this schema can be brought in
line via `alembic stamp head` instead of `upgrade head`; the backend handles
this automatically on startup.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-05-26 00:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cameras",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("rtsp_url", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column(
            "recording_mode",
            sa.String(length=20),
            nullable=False,
            server_default="off",
        ),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "username",
            sa.String(length=100),
            nullable=False,
            unique=True,
            index=True,
        ),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "is_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
    )

    op.create_table(
        "recordings",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "camera_id",
            sa.Integer(),
            sa.ForeignKey("cameras.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "file_path", sa.String(length=500), nullable=False, unique=True
        ),
        sa.Column("started_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column(
            "size_bytes",
            sa.BigInteger(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )


def downgrade() -> None:
    op.drop_table("recordings")
    op.drop_table("users")
    op.drop_table("cameras")
