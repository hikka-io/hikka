from app.models import Article, ArticleComment
from app.database import sessionmanager
from sqlalchemy import select, update
from app.utils import get_settings
import asyncio


async def fix_deleted_article_comments():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        articles = await session.scalars(
            select(Article).filter(Article.deleted == True)  # noqa: E712
        )

        for article in articles.unique():
            await session.execute(
                update(ArticleComment)
                .filter(ArticleComment.content == article)
                .values(private=True)
            )

            await session.commit()

            print(f"Hide comments for deleted article {article.title}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_deleted_article_comments())
