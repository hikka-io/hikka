from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import with_expression
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
    get_my_score_subquery,
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


async def get_article_by_slug(
    session: AsyncSession, slug: str, request_user: User
):
    return await session.scalar(
        select(Article)
        .filter(Article.slug == slug)
        .filter(Article.deleted == False)  # noqa: E712
        .options(joinedload(Article.author))
        .options(
            with_expression(
                Article.my_score,
                get_my_score_subquery(
                    Article, constants.CONTENT_ARTICLE, request_user
                ),
            )
        )
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

        if not await get_article_by_slug(session, slug, user):
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

    # Simple hack to init my_score with 0
    await session.refresh(article)

    return article


async def update_article(
    session: AsyncSession,
    article: Article,
    args: ArticleArgs,
    user: User,
    content: Anime | Manga | Novel | None = None,
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

    delete_old_content = False
    add_new_content = False

    # Get old content
    # TODO: find better way to handle this
    old_article_content = await session.scalar(
        select(ArticleContent).filter(ArticleContent.article_id == article.id)
    )

    if old_article_content:
        if content:
            if old_article_content.content_id != content.id:
                delete_old_content = True
                add_new_content = True

        else:
            delete_old_content = True

    if not old_article_content and content:
        add_new_content = True

    if delete_old_content:
        before["content"] = {
            "content_type": old_article_content.content_type,
            "content_id": str(old_article_content.content_id),
        }

        # Here we set after content to none
        # If add_new_content is False it will stay this way
        after["content"] = None

        # Delete old article content to keep things clean
        await session.delete(old_article_content)

    # And create new content if needed
    if add_new_content:
        article_content = ArticleContent(
            **{
                "content_type": args.content.content_type,
                "content_id": content.id,
                "article": article,
            }
        )

        after["content"] = {
            "content_type": args.content.content_type,
            "content_id": content.reference,
        }

        session.add(article_content)

    article.updated = utcnow()
    session.add(article)
    await session.commit()

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
        select(Article)
        .options(joinedload(Article.author))
        .options(
            with_expression(
                Article.my_score,
                get_my_score_subquery(
                    Article, constants.CONTENT_ARTICLE, request_user
                ),
            )
        ),
        request_user,
        args,
        session,
    )

    return await session.scalars(
        query.order_by(*build_articles_order_by(args.sort))
        .limit(limit)
        .offset(offset)
    )
