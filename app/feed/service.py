from app.models import Collection, Article, Comment, User, Feed
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_expression
from sqlalchemy.orm import joinedload
from collections import defaultdict
from sqlalchemy import select, case
from app.utils import path_to_uuid
from .schemas import FeedArgs
from app import constants

from app.service import (
    collections_load_options,
    get_followed_user_ids,
    get_my_score_subquery,
)

# TODO: remove me
from app.articles.service import load_articles_content
from app.comments.schemas import CommentNode


async def load_feed_collections(
    session: AsyncSession,
    content_ids: list,
    followed_user_ids: list,
    request_user: User | None,
):
    collections = await session.scalars(
        collections_load_options(
            select(Collection)
            .filter(
                Collection.id.in_(content_ids),
                Collection.visibility == constants.COLLECTION_PUBLIC,
                Collection.deleted == False,  # noqa: E712
            )
            .options(
                joinedload(Collection.author).with_expression(
                    User.is_followed,
                    case((User.id.in_(followed_user_ids), True), else_=False),
                )
            ),
            request_user,
            True,
        )
    )

    return collections.unique()


async def load_feed_articles(
    session: AsyncSession,
    content_ids: list,
    followed_user_ids: list,
    request_user: User | None,
):
    articles = await session.scalars(
        select(Article)
        .filter(
            Article.id.in_(content_ids),
            Article.category != constants.ARTICLE_SYSTEM,
            Article.draft == False,  # noqa: E712
        )
        .options(
            joinedload(Article.author).options(
                with_expression(
                    User.is_followed,
                    case((User.id.in_(followed_user_ids), True), else_=False),
                )
            )
        )
        .options(
            with_expression(
                Article.my_score,
                get_my_score_subquery(
                    Article, constants.CONTENT_ARTICLE, request_user
                ),
            )
        ),
    )

    # TODO: remove load_articles_content
    return await load_articles_content(session, articles.unique().all())


async def load_feed_comments(session: AsyncSession, content_ids: list):
    comments = await session.scalars(
        select(Comment).filter(
            Comment.hidden == False,  # noqa: E712
            Comment.private == False,  # noqa: E712
            Comment.deleted == False,  # noqa: E712
            Comment.id.in_(content_ids),
        )
    )

    return [
        CommentNode.create(path_to_uuid(comment.reference), comment)
        for comment in comments
    ]


async def get_user_feed(
    session: AsyncSession, request_user: User | None, args: FeedArgs
) -> User:
    followed_user_ids = await get_followed_user_ids(session, request_user)

    feed_query = (
        select(Feed)
        .order_by(
            Feed.deleted == False,  # noqa: E712
            Feed.created.desc(),
        )
        .limit(20)
    )

    if args.content_type:
        feed_query = feed_query.filter(Feed.content_type == args.content_type)

    if args.before:
        feed_query = feed_query.filter(
            Feed.created < args.before.replace(tzinfo=None)
        )

    feed = await session.scalars(feed_query)

    content_ids = defaultdict(list)
    tmp_feed = []

    for entry in feed:
        content_ids[entry.content_type].append(entry.content_id)
        tmp_feed.append(
            {
                "content_type": entry.content_type,
                "content_id": entry.content_id,
                "created": entry.created,
            }
        )

    result = []

    if "article" in content_ids:
        result += await load_feed_articles(
            session,
            content_ids["article"],
            followed_user_ids,
            request_user,
        )

    if "collection" in content_ids:
        result += await load_feed_collections(
            session,
            content_ids["collection"],
            followed_user_ids,
            request_user,
        )

    if "comment" in content_ids:
        result += await load_feed_comments(session, content_ids["comment"])

    return sorted(result, key=lambda x: x.created, reverse=True)
