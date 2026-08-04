from app.common.service.score import get_user_list_score
from app.database import sessionmanager
from app.models import Review, User
from app.utils import get_settings
from sqlalchemy import select
import asyncio


async def fix_review_scores():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        reviews = await session.scalars(select(Review))

        for review in reviews:
            if not (
                author := await session.scalar(
                    select(User).filter(User.id == review.author_id)
                )
            ):
                continue

            review.score = await get_user_list_score(
                session, review.content_type, review.content_id, author
            )

            if session.is_modified(review):
                print(f"Fixed score for review {review.id}")

        await session.commit()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_review_scores())
