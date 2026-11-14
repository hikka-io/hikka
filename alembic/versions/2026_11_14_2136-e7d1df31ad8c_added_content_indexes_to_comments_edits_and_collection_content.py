"""Added content indexes to comments, edits and collection content

Revision ID: e7d1df31ad8c
Revises: 9159463551d3
Create Date: 2026-11-14 21:36:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "e7d1df31ad8c"
down_revision = "9159463551d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_comments_content",
        "service_comments",
        ["content_type", "content_id"],
    )

    op.create_index(
        "ix_edits_content",
        "service_edits",
        ["content_type", "content_id"],
    )

    op.create_index(
        "ix_collection_content_content",
        "service_collection_content",
        ["content_type", "content_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_collection_content_content",
        table_name="service_collection_content",
    )

    op.drop_index("ix_edits_content", table_name="service_edits")
    op.drop_index("ix_comments_content", table_name="service_comments")
