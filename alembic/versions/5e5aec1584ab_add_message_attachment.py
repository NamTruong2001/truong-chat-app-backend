"""add message attachment

Revision ID: 5e5aec1584ab
Revises: 7f3e251d5478
Create Date: 2023-09-29 22:25:05.043030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e5aec1584ab'
down_revision = '7f3e251d5478'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("attachment",
                    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column("file_name", sa.String(100)),
                    sa.Column("original_file_name", sa.String(50)),
                    sa.Column("message_id", sa.Integer, sa.ForeignKey("messages.id")))


def downgrade() -> None:
    pass
