from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload

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
        .options(joinedload(History.user))
        .order_by(desc(History.updated), desc(History.created))
        .limit(limit)
        .offset(offset)
    )


async def get_history_count(session: AsyncSession) -> int:
    return await session.scalar(select(func.count(History.id)))


async def get_history(session: AsyncSession, limit: int, offset: int) -> User:
    """Get history"""

    return await session.scalars(
        select(History)
        .options(joinedload(History.user))
        .order_by(desc(History.updated), desc(History.created))
        .limit(limit)
        .offset(offset)
    )
