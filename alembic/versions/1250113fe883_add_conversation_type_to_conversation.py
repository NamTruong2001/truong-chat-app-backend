"""add conversation type to conversation

Revision ID: 1250113fe883
Revises: 540d38af2055
Create Date: 2023-09-19 17:02:58.854073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1250113fe883'
down_revision = '540d38af2055'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("conversation", sa.Column("type", sa.Enum("private", "group")))


def downgrade() -> None:
    op.drop_column("conversation", "type")
