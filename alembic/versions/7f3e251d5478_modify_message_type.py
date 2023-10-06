"""modify message type

Revision ID: 7f3e251d5478
Revises: 1250113fe883
Create Date: 2023-09-22 09:47:21.702225

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7f3e251d5478'
down_revision = '1250113fe883'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("messages", type_=sa.Enum('text', "image", "video", "voice", "document", "system"),
                    column_name="message_type")


def downgrade() -> None:
    op.alter_column("messages",
                    type_=sa.Column("message_type", sa.Enum('text', 'image', 'video'), column_name="message_type"))
