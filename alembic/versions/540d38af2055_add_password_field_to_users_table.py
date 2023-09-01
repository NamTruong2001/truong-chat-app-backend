"""add password field to users table

Revision ID: 540d38af2055
Revises: f622b0b821b5
Create Date: 2023-08-31 13:15:57.423817

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '540d38af2055'
down_revision = 'f622b0b821b5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password", sa.String(50)))


def downgrade() -> None:
    op.drop_column("users", "password")
