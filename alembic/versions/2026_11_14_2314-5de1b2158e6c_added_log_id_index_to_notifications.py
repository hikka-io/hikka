"""Added log_id index to notifications

Revision ID: 5de1b2158e6c
Revises: bb747eaa922e
Create Date: 2026-11-14 23:14:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "5de1b2158e6c"
down_revision = "bb747eaa922e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_service_notifications_log_id",
        "service_notifications",
        ["log_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_service_notifications_log_id",
        table_name="service_notifications",
    )
