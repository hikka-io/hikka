from sqlalchemy import select, desc, func, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import (
    History,
    Follow,
    User,
)


async def get_user_history_count(session: AsyncSession, user: User) -> int:
    return await session.scalar(
        select(func.count(History.id)).filter(History.user == user)
    )


async def get_user_history(
    session: AsyncSession, user: User, limit: int, offset: int
) -> ScalarResult[History]:
    """Get user history"""

    return await session.scalars(
        select(History)
        .filter(History.user == user)
        .options(joinedload(History.user))
        .order_by(desc(History.updated), desc(History.created))
        .limit(limit)
        .offset(offset)
    )


async def following_ids(session: AsyncSession, user: User):
    user_ids = await session.scalars(
        select(Follow.followed_user_id).filter(Follow.user == user)
    )

    user_ids = user_ids.all()
    user_ids.append(user.id)

    return user_ids


async def get_following_history_count(
    session: AsyncSession, user_ids: list
) -> int:
    return await session.scalar(
        select(func.count(History.id)).filter(History.user_id.in_(user_ids))
    )


async def get_following_history(
    session: AsyncSession, user_ids: list, limit: int, offset: int
) -> ScalarResult[History]:
    """Get following history"""

    return await session.scalars(
        select(History)
        .filter(History.user_id.in_(user_ids))
        .options(joinedload(History.user))
        .order_by(desc(History.updated), desc(History.created))
        .limit(limit)
        .offset(offset)
    )
