"""create_seen_status_table

Revision ID: e6b0a5cd95f1
Revises: 5e5aec1584ab
Create Date: 2024-01-08 21:49:53.226477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e6b0a5cd95f1"
down_revision = "5e5aec1584ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "read_status",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("last_seen_message_id", sa.Integer, sa.ForeignKey("messages.id")),
        sa.Column("conversation_id", sa.Integer, sa.ForeignKey("conversation.id")),
        sa.Column("read_at", sa.DateTime)
    )

def downgrade() -> None:
    op.drop_table("read_status")
