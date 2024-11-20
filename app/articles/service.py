from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from app.utils import utcnow, slugify
from app import constants
from uuid import uuid4

from app.models import (
    ArticleContent,
    Article,
    Anime,
    Manga,
    Novel,
    User,
)

from app.service import (
    get_user_by_username,
    create_log,
)

from .schemas import (
    ArticlesListArgs,
    ArticleArgs,
)


def build_articles_order_by(sort: list[str]):
    # TODO: Unified function for this stuff
    order_mapping = {
        "created": Article.created,
    }

    order_by = [
        (
            desc(order_mapping[field])
            if order == "desc"
            else asc(order_mapping[field])
        )
        for field, order in (entry.split(":") for entry in sort)
    ]

    return order_by


async def get_article_by_slug(session: AsyncSession, slug: str):
    return await session.scalar(
        select(Article)
        .filter(Article.slug == slug)
        .filter(Article.deleted == False)  # noqa: E712
        .options(joinedload(Article.author))
    )


async def create_article(
    session: AsyncSession,
    args: ArticleArgs,
    user: User,
    content: Anime | Manga | Novel | None = None,
):
    now = utcnow()

    max_attempts = 5
    attempts = 0

    # Since we deal with user generated content
    # we have to make sure slug is unique
    while True:
        slug = slugify(args.title, uuid4())

        # If we exceed out attempts limit we just generate random slug
        if attempts > max_attempts:
            slug = str(uuid4())
            break

        if not await get_article_by_slug(session, slug):
            break

        attempts += 1

    article = Article(
        **{
            "category": args.category,
            "draft": args.draft,
            "title": args.title,
            "text": args.text,
            "tags": args.tags,
            "deleted": False,
            "vote_score": 0,
            "author": user,
            "created": now,
            "updated": now,
            "slug": slug,
        }
    )

    session.add(article)

    if content:
        article_content = ArticleContent(
            **{
                "content_type": args.content.content_type,
                "content_id": content.id,
                "article": article,
            }
        )

        session.add(article_content)

    await session.commit()

    await create_log(
        session,
        constants.LOG_ARTICLE_CREATE,
        user,
        article.id,
        {
            "category": args.category,
            "draft": args.draft,
            "title": args.title,
            "text": args.text,
            "tags": args.tags,
            "content": (
                {
                    "content_type": args.content.content_type,
                    "content_id": content.reference,
                }
                if content
                else None
            ),
        },
    )

    return article


async def update_article(
    session: AsyncSession,
    article: Article,
    args: ArticleArgs,
    user: User,
):
    before = {}
    after = {}

    for key in ["category", "draft", "title", "text", "tags"]:
        old_value = getattr(article, key)
        new_value = getattr(args, key)

        if old_value != new_value:
            before[key] = old_value
            setattr(article, key, new_value)
            after[key] = new_value

    article.updated = utcnow()
    session.add(article)

    if before != {} and after != {}:
        await create_log(
            session,
            constants.LOG_ARTICLE_UPDATE,
            user,
            article.id,
            {
                "before": before,
                "after": after,
            },
        )

    return article


async def delete_article(session: AsyncSession, article: Article, user: User):
    article.deleted = True
    session.add(article)

    await session.commit()

    await create_log(
        session,
        constants.LOG_ARTICLE_DELETE,
        user,
        article.id,
    )

    return True


async def articles_list_filter(
    query: Select,
    request_user: User | None,
    args: ArticlesListArgs,
    session: AsyncSession,
):
    if args.author:
        author = await get_user_by_username(session, args.author)
        query = query.filter(Article.author == author)

    if args.draft and request_user:
        query = query.filter(
            Article.author == request_user,
            Article.draft == True,  # noqa: E712
        )

    query = query.filter(
        Article.deleted == False,  # noqa: E712
    )

    return query


async def get_articles_count(
    session: AsyncSession, request_user: User | None, args: ArticlesListArgs
) -> int:
    query = await articles_list_filter(
        select(func.count(Article.id)),
        request_user,
        args,
        session,
    )

    return await session.scalar(query)


async def get_articles(
    session: AsyncSession,
    request_user: User | None,
    args: ArticlesListArgs,
    limit: int,
    offset: int,
) -> list[Article]:
    query = await articles_list_filter(
        select(Article).options(joinedload(Article.author)),
        request_user,
        args,
        session,
    )

    return await session.scalars(
        query.order_by(*build_articles_order_by(args.sort))
        .limit(limit)
        .offset(offset)
    )
