from app.common.utils import find_document_images
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import auth_required
from app.common.service import get_images
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
    count_logs,
)

from app.utils import (
    check_user_permissions,
    round_datetime,
    utcnow,
)


def _can_use_category(user: User, category: str):
    """Check if user has permission to manage this category of articles"""
    return check_user_permissions(
        user, [constants.ARTICLE_CATEGORY_TO_PERMISSION[category]]
    )


async def validate_article(
    slug: str,
    request_user: User | None = Depends(auth_required(optional=True)),
    session: AsyncSession = Depends(get_session),
):
    if not (article := await service.get_article_by_slug(session, slug, request_user)):
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
        start_time=round_datetime(utcnow(), minutes=60, seconds=60),
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

    if not _can_use_category(author, args.category):
        raise Abort("articles", "bad-category")

    if args.trusted and not check_user_permissions(
        author, [constants.PERMISSION_ARTICLE_TRUSTED]
    ):
        raise Abort("articles", "not-trusted")

    image_nodes = find_document_images(args.document)

    if len(image_nodes) > 0:
        urls = list(set([entry["url"] for entry in image_nodes]))

        if not len(image_nodes) == len(urls):
            raise Abort("articles", "duplicate-image-url")

        images = await get_images(session, urls)
        images = images.all()

        if len(images) != len(urls):
            raise Abort("articles", "bad-image-url")

        for image in images:
            if image.attachment_content_id is not None:
                raise Abort("articles", "bad-image-url")

            if image.type != constants.UPLOAD_ATTACHMENT:
                raise Abort("articles", "bad-image-url")

            if image.user_id != author.id:
                raise Abort("articles", "bad-image-url")

            if image.deletion_request:
                raise Abort("articles", "bad-image-url")

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
    if article.author != user:
        if not check_user_permissions(
            user, [constants.PERMISSION_ARTICLE_UPDATE_MODERATOR]
        ):
            raise Abort("permission", "denied")

    # 1000 article updates per hour should be sensible limit
    updates_limit = 1000
    logs_count = await count_logs(
        session,
        constants.LOG_ARTICLE_UPDATE,
        user,
        start_time=round_datetime(utcnow(), minutes=60, seconds=60),
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

    if article.draft is False and args.draft is True:
        raise Abort("articles", "bad-draft")

    # We allow changing category for article drafts
    if article.draft is False and args.category != article.category:
        raise Abort("articles", "bad-category")

    # Yeah, this check is pointless considering previous one
    # But we keep it here just in case
    if not _can_use_category(user, args.category):
        raise Abort("articles", "bad-category")

    if args.trusted and not check_user_permissions(
        user, [constants.PERMISSION_ARTICLE_TRUSTED]
    ):
        raise Abort("articles", "not-trusted")

    image_nodes = find_document_images(args.document)

    if len(image_nodes) > 0:
        urls = list(set([entry["url"] for entry in image_nodes]))

        if not len(image_nodes) == len(urls):
            raise Abort("articles", "duplicate-image-url")

        images = await get_images(session, urls)
        images = images.all()

        if len(images) != len(urls):
            raise Abort("articles", "bad-image-url")

        for image in images:
            if image.attachment_content_id is not None:
                if (
                    image.attachment_content_type != constants.CONTENT_ARTICLE
                    or image.attachment_content_id != article.id
                ):
                    raise Abort("articles", "bad-image-url")

            if image.type != constants.UPLOAD_ATTACHMENT:
                raise Abort("articles", "bad-image-url")

            if image.user_id != article.author_id:
                raise Abort("articles", "bad-image-url")

            if image.deletion_request:
                raise Abort("articles", "bad-image-url")

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

    if args.content_slug and not await get_content_by_slug(
        session, args.content_type, args.content_slug
    ):
        raise Abort("content", "not-found")

    return args
