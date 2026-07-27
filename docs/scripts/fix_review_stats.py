from app.service import content_type_to_content_class
from sqlalchemy import select, update, func
from app.database import sessionmanager
from app.models import Comment, Review
from app.utils import get_settings
from app import constants
import asyncio


async def fix_review_stats():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        content_types = [
            constants.CONTENT_ANIME,
            constants.CONTENT_MANGA,
            constants.CONTENT_NOVEL,
        ]

        for content_type in content_types:
            print(f"Resetting review stats for {content_type}")

            await session.execute(
                update(content_type_to_content_class[content_type]).values(
                    review_stats={"yes": 0, "no": 0, "maybe": 0}
                )
            )

        # Filters here must match get_review_stats, hidden comments keep
        # their review row around until it's deleted
        review_counts = await session.execute(
            select(
                func.count(Review.id).label("count"),
                Review.content_type,
                Review.content_id,
                Review.recommended,
            )
            .join(Comment, Review.comment_id == Comment.id)
            .filter(
                Review.content_type.in_(content_types),
                Comment.hidden == False,  # noqa: E712
                Comment.deleted == False,  # noqa: E712
            )
            .group_by(
                Review.content_type,
                Review.content_id,
                Review.recommended,
            )
        )

        # One row per recommendation, so we group them by content here
        stats = {}

        for entry in review_counts:
            key = (entry.content_type, entry.content_id)
            stats.setdefault(key, {"yes": 0, "no": 0, "maybe": 0})
            stats[key][entry.recommended] = entry.count

        for (content_type, content_id), counts in stats.items():
            content_model = content_type_to_content_class[content_type]

            await session.execute(
                update(content_model)
                .filter(content_model.id == content_id)
                .values(review_stats=counts)
            )

            print(
                f"Updated review stats for {content_type} {content_id} ({counts})"
            )

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_review_stats())
