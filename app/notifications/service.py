from sqlalchemy import select, desc, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from app.models import (
    Notification,
    User,
)


async def get_unseen_notification(
    session: AsyncSession, notification_reference: UUID, user: User
) -> Notification | None:
    return await session.scalar(
        select(Notification).filter(
            Notification.id == notification_reference,
            Notification.seen == False,  # noqa: E712
            Notification.user == user,
        )
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
        select(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(desc(Notification.created))
        .limit(limit)
        .offset(offset)
    )


async def notification_seen(session: AsyncSession, notification: Notification):
    await session.execute(
        update(Notification)
        .filter(
            Notification.created <= notification.created,
            Notification.user_id == notification.user_id,
            Notification.seen == False,
        )
        .values(
            updated=datetime.utcnow(),
            seen=True,
        )
    )

    await session.commit()

    return True


async def get_unseen_count(session: AsyncSession, user: User):
    return await session.scalar(
        select(func.count(Notification.id)).filter(
            Notification.seen == False,  # noqa: E712
            Notification.user == user,
        )
    )
