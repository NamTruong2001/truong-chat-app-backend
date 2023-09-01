"""create user table

Revision ID: ccfd54b953fd
Revises: 
Create Date: 2023-08-31 10:08:11.570551

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccfd54b953fd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(200)),
        sa.Column("first_name", sa.String(200)),
        sa.Column("last_name", sa.String(200)),
        sa.Column("is_active", sa.Boolean),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("users")
