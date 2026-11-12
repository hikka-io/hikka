"""Added unique indexes to reads, favourites, votes and reviews

Revision ID: 9159463551d3
Revises: 332c7640054b
Create Date: 2026-11-12 21:11:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9159463551d3"
down_revision = "332c7640054b"
branch_labels = None
depends_on = None


VOTE_CONTENT_TABLES = {
    "collection": "service_collections",
    "comment": "service_comments",
    "article": "service_articles",
}


def remove_duplicates(table, columns, order_by, where="true"):
    # Parallel requests left duplicate rows which have to be removed
    # before unique index is created, first row in order_by is kept
    op.execute(
        f"""
        delete from {table}
        where id in (
            select id from (
                select id, row_number() over (
                    partition by {columns} order by {order_by}
                ) as position
                from {table}
                where {where}
            ) ranked
            where position > 1
        )
        """
    )


def upgrade() -> None:
    # Remember content with duplicate votes to recalculate its score
    op.execute(
        """
        create temporary table duplicate_votes as
        select distinct content_type, content_id
        from service_votes
        group by content_type, content_id, user_id
        having count(*) > 1
        """
    )

    # Updates went to one of the duplicates so we keep latest updated one
    remove_duplicates(
        "service_read",
        "content_type, content_id, user_id",
        "updated desc, created desc, id",
        "deleted = false",
    )

    remove_duplicates(
        "service_votes",
        "content_type, content_id, user_id",
        "updated desc, created desc, id",
    )

    # Favourites have nothing to update so we keep oldest active one
    remove_duplicates(
        "service_favourite",
        "content_type, content_id, user_id",
        "deleted, created, id",
    )

    # Vote score is sum of all votes so it counted removed duplicates too
    for content_type, table in VOTE_CONTENT_TABLES.items():
        op.execute(
            f"""
            update {table} target
            set vote_score = coalesce((
                select sum(score) from service_votes
                where content_type = '{content_type}'
                and content_id = target.id
            ), 0)
            where target.id in (
                select content_id from duplicate_votes
                where content_type = '{content_type}'
            )
            """
        )

    op.execute("drop table duplicate_votes")

    op.create_index(
        "uq_read_content_user",
        "service_read",
        ["content_type", "content_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("deleted = false"),
    )

    op.create_index(
        "uq_favourite_content_user",
        "service_favourite",
        ["content_type", "content_id", "user_id"],
        unique=True,
    )

    op.create_index(
        "uq_vote_content_user",
        "service_votes",
        ["content_type", "content_id", "user_id"],
        unique=True,
    )

    # There are no duplicate reviews so we don't remove anything here
    op.create_index(
        "uq_review_content_author",
        "service_reviews",
        ["content_type", "content_id", "author_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_review_content_author", table_name="service_reviews")
    op.drop_index("uq_vote_content_user", table_name="service_votes")
    op.drop_index("uq_favourite_content_user", table_name="service_favourite")
    op.drop_index("uq_read_content_user", table_name="service_read")
