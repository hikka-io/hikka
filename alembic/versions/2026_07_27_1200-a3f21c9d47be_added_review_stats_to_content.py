"""Added review stats to content

Revision ID: a3f21c9d47be
Revises: 80af30ce258a
Create Date: 2026-07-27 12:00:00.000000

"""

from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a3f21c9d47be"
down_revision = "80af30ce258a"
branch_labels = None
depends_on = None


tables = [
    ("service_content_anime", "anime"),
    ("service_content_manga", "manga"),
    ("service_content_novel", "novel"),
]


def upgrade() -> None:
    for table, content_type in tables:
        op.add_column(
            table,
            sa.Column(
                "review_stats",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default='{"yes": 0, "no": 0, "maybe": 0}',
            ),
        )

        # Backfill counts for reviews we already have, hidden and deleted
        # comments are skipped here same way get_review_stats does it
        op.execute(
            f"""
            UPDATE {table} SET review_stats = stats.counts
            FROM (
                SELECT
                    service_reviews.content_id AS content_id,
                    jsonb_build_object(
                        'yes', COUNT(*) FILTER (
                            WHERE service_reviews.recommended = 'yes'
                        ),
                        'no', COUNT(*) FILTER (
                            WHERE service_reviews.recommended = 'no'
                        ),
                        'maybe', COUNT(*) FILTER (
                            WHERE service_reviews.recommended = 'maybe'
                        )
                    ) AS counts
                FROM service_reviews
                JOIN service_comments
                    ON service_comments.id = service_reviews.comment_id
                WHERE service_reviews.content_type = '{content_type}'
                    AND service_comments.hidden = false
                    AND service_comments.deleted = false
                GROUP BY service_reviews.content_id
            ) AS stats
            WHERE {table}.id = stats.content_id
            """
        )


def downgrade() -> None:
    for table, _ in tables:
        op.drop_column(table, "review_stats")
