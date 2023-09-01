"""add username field to users table

Revision ID: f622b0b821b5
Revises: 9ddf2420e445
Create Date: 2023-08-31 11:25:00.280478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f622b0b821b5'
down_revision = '9ddf2420e445'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(50)))


def downgrade() -> None:
    op.drop_column("users", "username")
