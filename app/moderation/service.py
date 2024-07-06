from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload

from app.models import (
    Moderation,
    User,
)


async def get_moderation_count(session: AsyncSession) -> int:
    return await session.scalar(select(func.count(Moderation.id)))


async def get_moderation(
    session: AsyncSession, limit: int, offset: int
) -> User:
    """Get moderation history"""

    return await session.scalars(
        select(Moderation)
        .options(joinedload(Moderation.user))
        .order_by(desc(Moderation.created))
        .limit(limit)
        .offset(offset)
    )
