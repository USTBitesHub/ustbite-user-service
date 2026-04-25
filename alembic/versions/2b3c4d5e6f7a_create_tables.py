"""create_user_and_address_tables

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-04-25 00:00:00
"""
from alembic import op

revision = '2b3c4d5e6f7a'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # asyncpg requires ONE statement per op.execute() call

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE department_enum AS ENUM (
                'IT', 'HR', 'Finance', 'Operations', 'Design', 'Management'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            phone VARCHAR,
            department department_enum NOT NULL,
            floor_number VARCHAR,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ,
            UNIQUE (employee_id),
            UNIQUE (email)
        )
    """)

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_users_employee_id ON users(employee_id)"
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)"
    )

    op.execute("""
        CREATE TABLE IF NOT EXISTS floor_addresses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            label VARCHAR NOT NULL,
            floor_number VARCHAR NOT NULL,
            wing VARCHAR,
            building VARCHAR,
            is_default BOOLEAN DEFAULT FALSE
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS floor_addresses CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TYPE IF EXISTS department_enum")
