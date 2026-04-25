"""Convert users.department from department_enum to TEXT

Reason: SQLAlchemy Column(String) is used in the model.
Converts the existing PostgreSQL enum column to plain TEXT.

Revision ID: 5e6f7a8b9c0d
Revises: 4d5e6f7a8b9c
Create Date: 2026-04-25
"""
from alembic import op

revision = '5e6f7a8b9c0d'
down_revision = '4d5e6f7a8b9c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert enum-typed column to plain TEXT
    op.execute("ALTER TABLE users ALTER COLUMN department TYPE TEXT USING department::text")
    # Drop all variants of the stale PostgreSQL enum types
    op.execute("DROP TYPE IF EXISTS department_enum")
    op.execute("DROP TYPE IF EXISTS departmentenum")


def downgrade() -> None:
    op.execute("""
        CREATE TYPE department_enum AS ENUM (
            'IT', 'HR', 'Finance', 'Operations', 'Design', 'Management'
        )
    """)
    op.execute(
        "ALTER TABLE users ALTER COLUMN department TYPE department_enum "
        "USING department::department_enum"
    )
