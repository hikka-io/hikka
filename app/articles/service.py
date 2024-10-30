from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Article
from app.service import create_log
from .schemas import ArticleArgs
from app.utils import utcnow
from app import constants


async def create_article(
    session: AsyncSession,
    args: ArticleArgs,
    user: User,
):
    now = utcnow()

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
