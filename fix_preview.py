from app.common.utils import generate_preview
from app.database import sessionmanager
from app.utils import get_settings
from app.models import Article
from sqlalchemy import select
import asyncio


async def fix_preview():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        articles = await session.scalars(
            select(Article).order_by(Article.created.asc())
        )

        for article in articles.unique():
            article.preview = generate_preview(article.document)
            print(f"Updated preview for {article.title}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_preview())
