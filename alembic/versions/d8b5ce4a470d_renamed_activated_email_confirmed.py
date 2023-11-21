"""Renamed activated -> email_confirmed

Revision ID: d8b5ce4a470d
Revises: dacfd9a68976
Create Date: 2023-11-21 17:15:09.902212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d8b5ce4a470d"
down_revision = "dacfd9a68976"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "service_users", "activated", new_column_name="email_confirmed"
    )


def downgrade() -> None:
    op.alter_column(
        "service_users", "email_confirmed", new_column_name="activated"
    )
