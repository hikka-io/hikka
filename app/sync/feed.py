from sqlalchemy import select, exists, delete, func
from datetime import datetime, timedelta
from app.database import sessionmanager
from app import constants

from app.models import (
    Collection,
    Article,
    Comment,
    Review,
    Feed,
)


async def generate_feed_session(session, all: bool = False):
    if not all:
        last_feed_entry = await session.scalar(
            select(func.coalesce(func.max(Feed.created), datetime(2024, 1, 13)))
        )

        last_feed_entry -= timedelta(days=1)

    else:
        last_feed_entry = datetime(2024, 1, 13)

    articles_query = (
        select(Article)
        .filter(
            Article.created >= last_feed_entry,
            Article.deleted == False,  # noqa: E712
            Article.draft == False,  # noqa: E712
        )
        .order_by(Article.created.asc())
    )

    collections_query = (
        select(Collection)
        .filter(
            Collection.created >= last_feed_entry,
            Collection.visibility == constants.COLLECTION_PUBLIC,
            Collection.deleted == False,  # noqa: E712
        )
        .order_by(Collection.created.asc())
    )

    comments_query = (
        select(Comment)
        .filter(
            func.nlevel(Comment.path) == 1,
            Comment.updated >= last_feed_entry,
            Comment.private == False,  # noqa: E712
            Comment.deleted == False,  # noqa: E712
            Comment.hidden == False,  # noqa: E712
            ~Comment.review.has(),
        )
        .order_by(Comment.created.asc())
    )

    reviews_query = select(Review).filter(Review.updated >= last_feed_entry)

    for query in [
        articles_query,
        collections_query,
        comments_query,
        reviews_query,
    ]:
        content = await session.scalars(query)

        for entry in content.unique():
            name = entry.reference

            if feed := await session.scalar(
                select(Feed).filter(
                    Feed.content_type == entry.data_type,
                    Feed.content_id == entry.id,
                )
            ):
                feed.filter_content_type = entry.content_type
                feed.created = entry.created

                if entry.data_type == constants.CONTENT_ARTICLE:
                    feed.filter_category = entry.category

                    # Special hack for articles with no content
                    if entry.content_type is None:
                        feed.filter_content_type = constants.NO_CONTENT

                if session.is_modified(feed):
                    print(f"Added {entry.data_type} feed entry for {name}")

                continue

            feed = Feed(
                **{
                    "filter_content_type": entry.content_type,
                    "content_type": entry.data_type,
                    "author_id": entry.author_id,
                    "created": entry.created,
                    "content_id": entry.id,
                }
            )

            if entry.data_type == constants.CONTENT_ARTICLE:
                feed.filter_category = entry.category

            session.add(feed)

            if hasattr(entry, "title"):
                name = entry.title

            print(f"Added {entry.data_type} feed entry for {name}")

        # Handle comments which has been converted into reviews
        await session.execute(
            delete(Feed).where(
                Feed.content_type == constants.CONTENT_COMMENT,
                exists(
                    select(Review.id).where(
                        Review.comment_id == Feed.content_id
                    )
                ),
            )
        )

        # Handle deleted reviews
        await session.execute(
            delete(Feed).where(
                Feed.content_type == constants.CONTENT_REVIEW,
                ~exists(select(Review.id).where(Review.id == Feed.content_id)),
            )
        )

        await session.commit()


async def generate_feed():
    """Temporary way to generate feed"""

    async with sessionmanager.session() as session:
        await generate_feed_session(session)
