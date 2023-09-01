"""create conversation table

Revision ID: a6be04054f44
Revises: ccfd54b953fd
Create Date: 2023-08-31 10:13:28.278830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6be04054f44'
down_revision = 'ccfd54b953fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(50)),
        sa.Column("creator_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
        sa.Column("deleted_at", sa.DateTime)
    )


def downgrade() -> None:
    op.drop_table("conversation")
