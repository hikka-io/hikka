from app.common.service.collections import collections_load_options
from app.models import Collection, Article, Comment, User, Feed
from app.common.service.articles import load_articles_content
from sqlalchemy.orm import with_expression, joinedload
from app.common.schemas.comments import CommentNode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, or_
from collections import defaultdict
from app.utils import path_to_uuid
from .schemas import FeedArgs
from app import constants
from uuid import UUID

from app.service import (
    get_followed_user_ids,
    get_my_score_subquery,
)


async def load_feed_collections(
    session: AsyncSession,
    content_ids: list[UUID],
    followed_user_ids: list[UUID],
    request_user: User | None,
) -> list[Collection]:
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

    return collections.unique().all()


async def load_feed_articles(
    session: AsyncSession,
    content_ids: list[UUID],
    followed_user_ids: list[UUID],
    request_user: User | None,
) -> list[Article]:
    articles = await session.scalars(
        select(Article)
        .filter(
            Article.id.in_(content_ids),
            Article.category != constants.ARTICLE_SYSTEM,
            Article.deleted == False,  # noqa: E712
            Article.draft == False,  # noqa: E712
        )
        .options(
            joinedload(Article.author).with_expression(
                User.is_followed,
                case((User.id.in_(followed_user_ids), True), else_=False),
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


async def load_feed_comments(
    session: AsyncSession,
    content_ids: list[UUID],
    followed_user_ids: list[UUID],
    request_user: User | None,
) -> list[Comment]:
    comments = await session.scalars(
        select(Comment)
        .filter(
            Comment.hidden == False,  # noqa: E712
            Comment.private == False,  # noqa: E712
            Comment.deleted == False,  # noqa: E712
            Comment.id.in_(content_ids),
        )
        .options(
            joinedload(Comment.author).with_expression(
                User.is_followed,
                case((User.id.in_(followed_user_ids), True), else_=False),
            )
        )
        .options(
            with_expression(
                Comment.my_score,
                get_my_score_subquery(
                    Comment, constants.CONTENT_COMMENT, request_user
                ),
            )
        )
    )

    return [
        CommentNode.create(path_to_uuid(comment.reference), comment)
        for comment in comments
    ]


async def get_user_feed(
    session: AsyncSession, request_user: User | None, args: FeedArgs
) -> list[Collection | Article | Comment]:
    # List of followed users to load is_followed statuses and filtering
    followed_user_ids = await get_followed_user_ids(session, request_user)

    # Base feed filters
    user_feed_filter = (
        or_(
            Feed.user_id == request_user.id,
            Feed.user_id == None,  # noqa: E711
        )
        if request_user is not None
        else Feed.user_id == None  # noqa: E711
    )

    feed_query = (
        select(Feed)
        .filter(
            Feed.deleted == False,  # noqa: E712
            user_feed_filter,
        )
        .order_by(Feed.created.desc())
        .limit(20)
    )

    # TODO: remove me
    if args.content_type:
        feed_query = feed_query.filter(Feed.content_type == args.content_type)

    # Filter by feed content types
    if args.feed_content_types is not None:
        feed_query = feed_query.filter(
            Feed.content_type.in_(args.feed_content_types)
        )

    # General filters
    # Filter by followed users
    if args.only_followed:
        feed_query = feed_query.filter(Feed.author_id.in_(followed_user_ids))

    # Return older than
    if args.before:
        feed_query = feed_query.filter(
            Feed.created < args.before.replace(tzinfo=None)
        )

    # Content specific filters
    if args.collection_content_types:
        feed_query = feed_query.filter(
            or_(
                Feed.filter_content_type.in_(args.collection_content_types),
                Feed.content_type != constants.CONTENT_COLLECTION,
            )
        )

    if args.article_categories is not None:
        feed_query = feed_query.filter(
            or_(
                Feed.filter_category.in_(args.article_categories),
                Feed.content_type != constants.CONTENT_ARTICLE,
            )
        )

    if args.article_content_types is not None:
        feed_query = feed_query.filter(
            or_(
                Feed.filter_content_type.in_(args.article_content_types),
                Feed.content_type != constants.CONTENT_ARTICLE,
            )
        )

    if args.comment_content_types is not None:
        feed_query = feed_query.filter(
            or_(
                Feed.filter_content_type.in_(args.comment_content_types),
                Feed.content_type != constants.CONTENT_COMMENT,
            )
        )

    feed = await session.scalars(feed_query)

    content_ids = defaultdict(list)
    for entry in feed:
        content_ids[entry.content_type].append(entry.content_id)

    result = []

    for content_type, load_function in [
        (constants.CONTENT_COLLECTION, load_feed_collections),
        (constants.CONTENT_ARTICLE, load_feed_articles),
        (constants.CONTENT_COMMENT, load_feed_comments),
    ]:
        if content_type in content_ids:
            result += await load_function(
                session,
                content_ids[content_type],
                followed_user_ids,
                request_user,
            )

    return sorted(result, key=lambda x: x.created, reverse=True)
