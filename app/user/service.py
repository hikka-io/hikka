from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import timedelta
from app.utils import utcnow

from app.models import (
    Activity,
    User,
)


async def get_user_activity(session: AsyncSession, user: User) -> User:
    """Get user activity"""

    end = utcnow()
    start = end - timedelta(weeks=16)

    return await session.scalars(
        select(Activity)
        .filter(
            Activity.user == user,
            Activity.timestamp >= start,
            Activity.timestamp <= end,
        )
        .order_by(desc(Activity.timestamp))
    )


async def users_meilisearch(
    session: AsyncSession,
    meilisearch_result: dict,
):
    usernames = [user["username"] for user in meilisearch_result["list"]]

    # NOTE: we may need to preserve results order from Meilisearch here
    # For reference see anime_meilisearch_watch function

    return await session.scalars(
        select(User)
        .filter(User.username.in_(usernames))
        .order_by(desc(User.last_active))
    )
