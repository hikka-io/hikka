from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from datetime import timedelta
from app.utils import utcnow

from app.models import (
    Activity,
    History,
    User,
)


async def get_user_history_count(session: AsyncSession, user: User) -> int:
    return await session.scalar(
        select(func.count(History.id)).filter(History.user == user)
    )


async def get_user_history(
    session: AsyncSession, user: User, limit: int, offset: int
) -> User:
    """Get user history"""

    return await session.scalars(
        select(History)
        .filter(History.user == user)
        .order_by(desc(History.updated), desc(History.created))
        .limit(limit)
        .offset(offset)
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

    return await session.scalars(
        select(User)
        .filter(User.username.in_(usernames))
        .order_by(desc(User.last_active))
    )
