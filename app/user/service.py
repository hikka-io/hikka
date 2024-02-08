from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models import (
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
