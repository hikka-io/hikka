"""Renamed field

Revision ID: ccca6c061336
Revises: 198605b6007f
Create Date: 2025-01-03 21:38:09.615009

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ccca6c061336"
down_revision = "198605b6007f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "service_content_anime",
        "poster_id",
        new_column_name="image_id",
        existing_type=sa.Uuid(),
        existing_nullable=True,
    )

    op.drop_index(
        "ix_service_content_anime_poster_id", table_name="service_content_anime"
    )

    op.create_index(
        op.f("ix_service_content_anime_image_id"),
        "service_content_anime",
        ["image_id"],
        unique=False,
    )


def downgrade() -> None:
    op.alter_column(
        "service_content_anime",
        "image_id",
        new_column_name="poster_id",
        existing_type=sa.Uuid(),
        existing_nullable=True,
    )

    op.drop_index(
        "ix_service_content_anime_image_id", table_name="service_content_anime"
    )

    op.create_index(
        op.f("ix_service_content_anime_poster_id"),
        "service_content_anime",
        ["image_id"],
        unique=False,
    )
