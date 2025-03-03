from app.comments.service import generate_preview
from app.database import sessionmanager
from app.models import ArticleComment
from app.utils import get_settings
from sqlalchemy import select
import asyncio


async def fix_collection_comments():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        comments = await session.scalars(select(ArticleComment))

        for comment in comments:
            comment = await generate_preview(session, comment)
            print(f"Generated preview for {comment.id}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_collection_comments())
