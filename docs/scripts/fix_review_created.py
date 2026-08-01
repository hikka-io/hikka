from app.sync.feed import generate_feed_session
from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from app.utils import get_settings
from app.models import Review
from sqlalchemy import select
import asyncio


async def fix_review_created():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        reviews = await session.scalars(
            select(Review).options(joinedload(Review.comment))
        )

        for review in reviews:
            if review.comment.created != review.created:
                review.created = review.comment.created
                print(f"Fixed created for review {review.id}")

        await session.commit()

        await generate_feed_session(session, True)

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(fix_review_created())
