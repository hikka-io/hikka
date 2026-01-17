from app.service import content_type_to_content_class
from sqlalchemy import select, update, desc, func
from app.database import sessionmanager
from app.utils import get_settings
from app.models import Comment
from app import constants
import asyncio


async def fix_comments_count():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        for content_type in [
            constants.CONTENT_COLLECTION,
            constants.CONTENT_SYSTEM_EDIT,
            constants.CONTENT_ARTICLE,
            constants.CONTENT_ANIME,
            constants.CONTENT_MANGA,
            constants.CONTENT_NOVEL,
        ]:
            print(f"Resetting comment counts for {content_type}")

            await session.execute(
                update(content_type_to_content_class[content_type]).values(
                    comments_count_pagination=0,
                    comments_count=0,
                )
            )

        comment_counts = await session.execute(
            select(
                func.count(Comment.id).label("comments_count"),
                Comment.content_type,
                Comment.content_id,
            )
            .filter(
                Comment.hidden == False,  # noqa: E712
                Comment.deleted == False,  # noqa: E712
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

        comment_counts_pagination = await session.execute(
            select(
                func.count(Comment.id).label("comments_count_pagination"),
                Comment.content_type,
                Comment.content_id,
            )
            .filter(
                func.nlevel(Comment.path) == 1,
                Comment.hidden == False,  # noqa: E712
                Comment.deleted == False,  # noqa: E712
            )
            .group_by(
                Comment.content_type,
                Comment.content_id,
            )
            .order_by(desc("comments_count_pagination"))
        )

        for entry in comment_counts_pagination:
            content_model = content_type_to_content_class[entry.content_type]

            await session.execute(
                update(content_model)
                .filter(content_model.id == entry.content_id)
                .values(
                    comments_count_pagination=entry.comments_count_pagination
                )
            )

            print(
                f"Updated comments count pagination for {entry.content_type} {entry.content_id} ({entry.comments_count_pagination})"
            )

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_comments_count())
