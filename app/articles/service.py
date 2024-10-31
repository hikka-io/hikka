from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import utcnow, slugify
from app.models import User, Article
from app.service import create_log
from .schemas import ArticleArgs
from sqlalchemy import select
from app import constants
from uuid import uuid4


async def get_article_by_slug(session: AsyncSession, slug: str):
    return await session.scalar(select(Article).filter(Article.slug == slug))


async def create_article(
    session: AsyncSession,
    args: ArticleArgs,
    user: User,
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
