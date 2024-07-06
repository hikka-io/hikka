from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models import (
    Moderation,
    User,
)


async def get_moderation_count(session: AsyncSession) -> int:
    return await session.scalar(select(func.count(Moderation.id)))


async def get_moderation(
    session: AsyncSession, limit: int, offset: int
) -> User:
    """Get moderation log"""

    return await session.scalars(
        select(Moderation)
        .order_by(desc(Moderation.created))
        .limit(limit)
        .offset(offset)
    )


async def get_user_moderation_count(
    session: AsyncSession, user_id: User.id
) -> int:
    return await session.scalar(
        select(func.count(Moderation.id)).filter(Moderation.user_id == user_id)
    )


async def get_user_moderation(
    session: AsyncSession, user_id: User.id, limit: int, offset: int
) -> User:
    """Get user moderation log"""

    return await session.scalars(
        select(Moderation)
        .filter(Moderation.user_id == user_id)
        .order_by(desc(Moderation.created))
        .limit(limit)
        .offset(offset)
    )
