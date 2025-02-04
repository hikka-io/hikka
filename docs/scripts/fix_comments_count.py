from app.service import content_type_to_content_class
from sqlalchemy import select, update, desc, func
from app.database import sessionmanager
from app.utils import get_settings
from app.models import Comment
import asyncio


async def fix_comments_count():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        comment_counts = await session.execute(
            select(
                func.count(Comment.id).label("comments_count"),
                Comment.content_type,
                Comment.content_id,
            )
            .group_by(
                Comment.content_type,
                Comment.content_id,
            )
            .order_by(desc("comments_count"))
        )

        for entry in comment_counts:
            content_model = content_type_to_content_class[entry.content_type]

            await session.execute(
                update(content_model)
                .filter(content_model.id == entry.content_id)
                .values(comments_count=entry.comments_count)
            )

            print(
                f"Updated comments count for {entry.content_type} {entry.content_id} ({entry.comments_count})"
            )

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_comments_count())
