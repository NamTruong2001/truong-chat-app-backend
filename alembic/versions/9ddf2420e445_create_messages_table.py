"""create messages table

Revision ID: 9ddf2420e445
Revises: 71e685559df1
Create Date: 2023-08-31 10:46:21.515017

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9ddf2420e445'
down_revision = '71e685559df1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.Integer, sa.ForeignKey("conversation.id")),
        sa.Column("sender_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("message_type", sa.Enum('text', 'image', 'video')),
        sa.Column("message", sa.TEXT),
        sa.Column("created_at", sa.DateTime))


def downgrade() -> None:
    op.drop_table("messages")
