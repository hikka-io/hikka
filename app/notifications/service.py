from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models import (
    Notification,
    User,
)


async def get_user_notifications_count(
    session: AsyncSession, user: User
) -> int:
    return await session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.user_id == user.id
        )
    )


async def get_user_notifications(
    session: AsyncSession, user: User, limit: int, offset: int
) -> User:
    """Get user notifications"""

    return await session.scalars(
        select(Notification).filter(Notification.user_id == user.id)
        # .order_by(desc(Notification.created))
        # .limit(limit)
        # .offset(offset)
    )
