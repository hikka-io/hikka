"""Added mal_id to characters and people

Revision ID: f4a3c9d27b61
Revises: 80af30ce258a
Create Date: 2026-07-26 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f4a3c9d27b61"
down_revision = "80af30ce258a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "service_content_characters",
        sa.Column("mal_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_service_content_characters_mal_id"),
        "service_content_characters",
        ["mal_id"],
        unique=False,
    )

    op.add_column(
        "service_content_people",
        sa.Column("mal_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_service_content_people_mal_id"),
        "service_content_people",
        ["mal_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_service_content_people_mal_id"),
        table_name="service_content_people",
    )
    op.drop_column("service_content_people", "mal_id")

    op.drop_index(
        op.f("ix_service_content_characters_mal_id"),
        table_name="service_content_characters",
    )
    op.drop_column("service_content_characters", "mal_id")
