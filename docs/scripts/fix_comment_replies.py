from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmanager
from sqlalchemy import select, func
from app.utils import get_settings
from app.models import Comment
import asyncio


async def count_replies(session: AsyncSession, comment: Comment):
    return await session.scalar(
        select(func.count(Comment.id)).filter(
            Comment.path.descendant_of(comment.path),
            Comment.deleted == False,  # noqa: E712
            Comment.hidden == False,  # noqa: E712
            Comment.id != comment.id,
        )
    )


async def fix_comment_replies():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        comments = await session.scalars(select(Comment))

        for comment in comments:
            comment.total_replies = await count_replies(session, comment)

            if session.is_modified(comment):
                print(
                    f"Fixed replies count for {comment.id}: {comment.total_replies}"
                )

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_comment_replies())
