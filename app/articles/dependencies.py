from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.database import get_session
from app.models import User, Article
from app.errors import Abort
from fastapi import Depends
from app import constants
from . import service

from .schemas import (
    ArticlesListArgs,
    ArticleArgs,
)

from app.service import (
    get_user_by_username,
    get_content_by_slug,
    get_upload_by_url,
    count_logs,
)

from app.utils import (
    check_user_permissions,
    round_datetime,
    utcnow,
)


def can_use_category(user: User, category: str):
    available_categories = {
        constants.ROLE_USER: [],
        constants.ROLE_MODERATOR: [constants.ARTICLE_NEWS],
        constants.ROLE_ADMIN: [
            constants.ARTICLE_NEWS,
            constants.ARTICLE_SYSTEM,
        ],
    }.get(user.role, [])

    return category in available_categories


async def validate_article(
    slug: str,
    request_user: User | None = Depends(auth_required(optional=True)),
    session: AsyncSession = Depends(get_session),
):
    if not (
        article := await service.get_article_by_slug(
            session, slug, request_user
        )
    ):
        raise Abort("articles", "not-found")

    return article


async def validate_article_content(
    args: ArticleArgs,
    session: AsyncSession = Depends(get_session),
):
    content = None

    if args.content and not (
        content := await get_content_by_slug(
            session, args.content.content_type, args.content.slug
        )
    ):
        raise Abort("content", "not-found")

    return content


async def validate_article_create(
    args: ArticleArgs,
    session: AsyncSession = Depends(get_session),
    author: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_ARTICLE_CREATE],
            scope=[constants.SCOPE_CREATE_ARTICLE],
        )
    ),
):
    # TODO: Make reusable code for rate limit (?)

    # For now we will allow 10 articles per hour
    articles_limit = 10
    logs_count = await count_logs(
        session,
        constants.LOG_ARTICLE_CREATE,
        author,
        start_time=round_datetime(utcnow(), hours=1),
    )

    if (
        author.role
        not in [
            constants.ROLE_ADMIN,
            constants.ROLE_MODERATOR,
        ]
        and logs_count > articles_limit
    ):
        raise Abort("system", "rate-limit")

    if not can_use_category(author, args.category):
        raise Abort("articles", "bad-category")

    if args.cover is not None:
        if not (upload := await get_upload_by_url(session, args.cover)):
            raise Abort("articles", "cover-not-found")

        if (
            not upload.image.uploaded
            or upload.type != constants.UPLOAD_ATTACHMENT
            or upload.image.deletion_request
            or upload.user_id != author.id
            or upload.image.used
        ):
            raise Abort("articles", "bad-cover")

    return author


async def validate_article_update(
    args: ArticleArgs,
    session: AsyncSession = Depends(get_session),
    article: Article = Depends(validate_article),
    user: User = Depends(
        auth_required(
            permissions=[constants.PERMISSION_ARTICLE_UPDATE],
            scope=[constants.SCOPE_UPDATE_ARTICLE],
        )
    ),
):
    # Special flag in case article is being updated by moderator
    is_moderator = False

    if article.author != user:
        if not check_user_permissions(
            user, [constants.PERMISSION_ARTICLE_UPDATE_MODERATOR]
        ):
            raise Abort("permission", "denied")

        is_moderator = True

    # 1000 article updates per hour should be sensible limit
    updates_limit = 1000
    logs_count = await count_logs(
        session,
        constants.LOG_ARTICLE_UPDATE,
        user,
        start_time=round_datetime(utcnow(), hours=1),
    )

    if (
        user.role
        not in [
            constants.ROLE_ADMIN,
            constants.ROLE_MODERATOR,
        ]
        and logs_count > updates_limit
    ):
        raise Abort("system", "rate-limit")

    # We leave it here for now, maybe change in the future
    if args.category != article.category:
        raise Abort("articles", "bad-category")

    # Yeah, this check is pointless considering previous one
    # But we keep it here just in case
    if not can_use_category(user, args.category):
        raise Abort("articles", "bad-category")

    if args.cover is not None:
        print(args.cover)
        if not (upload := await get_upload_by_url(session, args.cover)):
            raise Abort("articles", "cover-not-found")

        if (
            not upload.image.uploaded
            or upload.image.deletion_request
            or upload.type != constants.UPLOAD_ATTACHMENT
        ):
            raise Abort("articles", "bad-cover")

        # Check to allow moderator to change image
        if not is_moderator and upload.user_id != user.id:
            raise Abort("articles", "bad-cover")

        # Make sure we let user update his article with same image
        if upload.image.used and upload.image != article.cover_image:
            raise Abort("articles", "bad-cover")

    return article


async def validate_article_delete(
    article: Article = Depends(validate_article),
    user: User = Depends(auth_required()),
):
    if article.author != user and not check_user_permissions(
        user, [constants.PERMISSION_ARTICLE_DELETE_MODERATOR]
    ):
        raise Abort("permission", "denied")

    return article


async def validate_articles_list_args(
    args: ArticlesListArgs,
    session: AsyncSession = Depends(get_session),
):
    if args.author and not await get_user_by_username(session, args.author):
        raise Abort("articles", "author-not-found")

    return args
