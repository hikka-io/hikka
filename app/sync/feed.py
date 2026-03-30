from app.models import Article, Collection, Comment, Feed
from app.database import sessionmanager
from sqlalchemy import select, func
from app import constants


async def generate_feed():
    """Temporary way to generate feed"""

    async with sessionmanager.session() as session:
        articles_query = (
            select(Article)
            .filter(
                Article.deleted == False,  # noqa: E712
                Article.draft == False,  # noqa: E712
            )
            .order_by(Article.created.asc())
        )

        collections_query = (
            select(Collection)
            .filter(
                Collection.visibility == constants.COLLECTION_PUBLIC,
                Collection.deleted == False,  # noqa: E712
            )
            .order_by(Collection.created.asc())
        )

        comments_query = (
            select(Comment)
            .filter(
                func.nlevel(Comment.path) == 1,
                Comment.hidden == False,  # noqa: E712
                Comment.private == False,  # noqa: E712
                Comment.deleted == False,  # noqa: E712
            )
            .order_by(Comment.created.asc())
        )

        for query in [articles_query, collections_query, comments_query]:
            content = await session.scalars(query)

            for entry in content.unique():
                if await session.scalar(
                    select(Feed).filter(
                        Feed.content_type == entry.data_type,
                        Feed.content_id == entry.id,
                    )
                ):
                    continue

                feed = Feed(
                    **{
                        "content_type": entry.data_type,
                        "author_id": entry.author_id,
                        "created": entry.created,
                        "content_id": entry.id,
                    }
                )

                session.add(feed)

                name = entry.reference

                if hasattr(entry, "title"):
                    name = entry.title

                print(f"Added {entry.data_type} feed entry for {name}")

            await session.commit()
