"""Added deleted field to clients

Revision ID: 332c7640054b
Revises: 93ce5aa3766f
Create Date: 2026-10-16 13:44:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "332c7640054b"
down_revision = "93ce5aa3766f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "service_clients",
        sa.Column(
            "deleted", sa.Boolean(), server_default="false", nullable=False
        ),
    )
    op.create_index(
        op.f("ix_service_clients_deleted"),
        "service_clients",
        ["deleted"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_service_clients_deleted"), table_name="service_clients"
    )
    op.drop_column("service_clients", "deleted")
