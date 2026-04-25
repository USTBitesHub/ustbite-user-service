"""add_password_hash_to_users

Revision ID: 4d5e6f7a8b9c
Revises: 2b3c4d5e6f7a
Create Date: 2026-04-25
"""
from alembic import op

revision = '4d5e6f7a8b9c'
down_revision = '2b3c4d5e6f7a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE users DROP COLUMN IF EXISTS password_hash"
    )
