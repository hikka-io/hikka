"""Renamed artifact -> digest

Revision ID: 4118892f8a06
Revises: 0dc2df191429
Create Date: 2026-02-08 17:30:06.175592

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "4118892f8a06"
down_revision = "0dc2df191429"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("service_artifacts", "service_digests")


def downgrade() -> None:
    op.rename_table("service_digests", "service_artifacts")
