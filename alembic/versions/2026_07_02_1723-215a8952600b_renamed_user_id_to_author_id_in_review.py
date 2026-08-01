"""Renamed user_id to author_id in review

Revision ID: 215a8952600b
Revises: 685836147116
Create Date: 2026-07-02 17:23:06.460217

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "215a8952600b"
down_revision = "685836147116"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "service_reviews",
        "user_id",
        new_column_name="author_id",
        existing_type=sa.Uuid(),
        existing_nullable=True,
    )

    op.drop_index("ix_service_reviews_user_id", table_name="service_reviews")

    op.create_index(
        op.f("ix_service_reviews_author_id"),
        "service_reviews",
        ["author_id"],
        unique=False,
    )


def downgrade() -> None:
    op.alter_column(
        "service_reviews",
        "author_id",
        new_column_name="user_id",
        existing_type=sa.Uuid(),
        existing_nullable=True,
    )

    op.drop_index("ix_service_reviews_author_id", table_name="service_reviews")

    op.create_index(
        op.f("ix_service_reviews_user_id"),
        "service_reviews",
        ["user_id"],
        unique=False,
    )
