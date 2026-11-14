"""Added author, email and search update indexes

Revision ID: bb747eaa922e
Revises: e7d1df31ad8c
Create Date: 2026-11-14 22:02:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bb747eaa922e"
down_revision = "e7d1df31ad8c"
branch_labels = None
depends_on = None


COLUMN_INDEXES = [
    ("ix_service_edits_author_id", "service_edits", "author_id"),
    ("ix_service_comments_author_id", "service_comments", "author_id"),
    ("ix_service_favourite_user_id", "service_favourite", "user_id"),
    (
        "ix_service_content_companies_anime_anime_id",
        "service_content_companies_anime",
        "anime_id",
    ),
]

# Partial indexes only hold rows waiting for search sync
SEARCH_UPDATE_INDEXES = [
    ("ix_characters_search_update", "service_content_characters", "content_id"),
    ("ix_companies_search_update", "service_content_companies", "content_id"),
    ("ix_people_search_update", "service_content_people", "content_id"),
    ("ix_anime_search_update", "service_content_anime", "content_id"),
    ("ix_manga_search_update", "service_content_manga", "content_id"),
    ("ix_novel_search_update", "service_content_novel", "content_id"),
    ("ix_articles_search_update", "service_articles", "id"),
    ("ix_users_search_update", "service_users", "id"),
]


def upgrade() -> None:
    for name, table, column in COLUMN_INDEXES:
        op.create_index(name, table, [column])

    # Lookups use lower(email) so plain email index was never used
    op.drop_index("ix_service_users_email", table_name="service_users")

    op.create_index(
        "ix_lower_email",
        "service_users",
        [sa.text("lower(email)")],
        unique=True,
    )

    for name, table, column in SEARCH_UPDATE_INDEXES:
        op.create_index(
            name,
            table,
            [column],
            postgresql_where=sa.text("needs_search_update"),
        )


def downgrade() -> None:
    for name, table, _ in SEARCH_UPDATE_INDEXES:
        op.drop_index(name, table_name=table)

    op.drop_index("ix_lower_email", table_name="service_users")
    op.create_index("ix_service_users_email", "service_users", ["email"])

    for name, table, _ in COLUMN_INDEXES:
        op.drop_index(name, table_name=table)
