from app.database import sessionmanager
from app.utils import get_settings
from app.comments import service
from app.models import Comment
from sqlalchemy import select
import asyncio


async def fix_comments_preview():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        comments = await session.scalars(
            select(Comment).filter(Comment.preview == {})
        )

        for comment in comments:
            await service.generate_preview(session, comment)
            print(f"Generated preview for comment {comment.id}")

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_comments_preview())
