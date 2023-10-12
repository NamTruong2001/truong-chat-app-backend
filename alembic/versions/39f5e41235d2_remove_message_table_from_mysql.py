"""remove message table from mysql

Revision ID: 39f5e41235d2
Revises: 5e5aec1584ab
Create Date: 2023-10-12 09:03:32.057127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39f5e41235d2'
down_revision = '5e5aec1584ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("attachment")
    op.drop_table("messages")


def downgrade() -> None:
    op.create_table("attachment",
                    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column("file_name", sa.String(100)),
                    sa.Column("original_file_name", sa.String(50)),
                    sa.Column("message_id", sa.Integer, sa.ForeignKey("messages.id")))
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.Integer, sa.ForeignKey("conversation.id")),
        sa.Column("sender_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("message_type", sa.Enum('text', "image", "video", "voice", "document", "system"),),
        sa.Column("message", sa.TEXT),
        sa.Column("created_at", sa.DateTime)
    )
