"""create participants table

Revision ID: 71e685559df1
Revises: a6be04054f44
Create Date: 2023-08-31 10:29:01.035879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71e685559df1'
down_revision = 'a6be04054f44'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "participants",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.Integer, sa.ForeignKey("conversation.id")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("type", sa.Enum("creator", "member")),
        sa.Column("updated_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime)
    )


def downgrade() -> None:
    op.drop_table("participants")
