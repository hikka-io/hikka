from sqlalchemy import select, desc, update, func, distinct, ScalarResult
from sqlalchemy.dialects.postgresql import aggregate_order_by, array_agg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.utils import utcnow
from datetime import date
from . import grouping
from uuid import UUID

from app.models import (
    Notification,
    User,
)


async def get_notification(
    session: AsyncSession, notification_reference: UUID, user: User
) -> Notification | None:
    return await session.scalar(
        select(Notification)
        .filter(
            Notification.id == notification_reference,
            Notification.user == user,
        )
        .options(selectinload(Notification.initiator_user))
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
) -> ScalarResult[Notification]:
    """Get user notifications"""

    return await session.scalars(
        select(Notification)
        .filter(Notification.user_id == user.id)
        .options(selectinload(Notification.initiator_user))
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
            Notification.seen == False,  # noqa: E712
        )
        .values(
            updated=utcnow(),
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


def _user_groups_query(user: User):
    subkey = grouping.group_subkey().label("subkey")
    day = grouping.group_day().label("day")

    return (
        select(
            Notification.notification_type,
            subkey,
            day,
            func.max(Notification.created).label("created"),
            func.count(Notification.id).label("count"),
            func.count(Notification.id)
            .filter(Notification.seen == False)  # noqa: E712
            .label("unseen"),
            func.count(distinct(grouping.group_actor())).label("actors"),
            func.count(distinct(grouping.group_target())).label("targets"),
            array_agg(
                aggregate_order_by(Notification.id, desc(Notification.created))
            )[1 : grouping.GROUP_NOTIFICATIONS_LIMIT].label("ids"),
        )
        .filter(Notification.user_id == user.id)
        .group_by(Notification.notification_type, subkey, day)
    )


async def get_user_notification_groups_count(
    session: AsyncSession, user: User
) -> int:
    return await session.scalar(
        select(func.count()).select_from(_user_groups_query(user).subquery())
    )


async def get_user_notification_groups(
    session: AsyncSession, user: User, limit: int, offset: int
) -> list[dict]:
    """Notification groups, most recently active first, each with its newest members."""

    rows = (
        await session.execute(
            _user_groups_query(user)
            .order_by(
                desc("created"),
                Notification.notification_type,
                "subkey",
            )
            .limit(limit)
            .offset(offset)
        )
    ).all()

    ids = [notification_id for row in rows for notification_id in row.ids]
    notifications = {
        notification.id: notification
        for notification in await session.scalars(
            select(Notification)
            .filter(Notification.id.in_(ids))
            .options(selectinload(Notification.initiator_user))
        )
    }

    return [
        {
            "reference": grouping.make_group_reference(
                row.notification_type, row.subkey, row.day
            ),
            "notification_type": row.notification_type,
            "created": row.created,
            "count": row.count,
            "unseen": row.unseen,
            "actors": row.actors,
            "targets": row.targets,
            "notifications": [
                notifications[notification_id]
                for notification_id in row.ids
                if notification_id in notifications
            ],
        }
        for row in rows
    ]


async def notification_group_seen(
    session: AsyncSession,
    user: User,
    notification_type: str,
    subkey: str,
    day: date,
) -> None:
    """Marks only the members of one group as seen (unlike `notification_seen`)."""

    await session.execute(
        update(Notification)
        .filter(
            Notification.user_id == user.id,
            Notification.notification_type == notification_type,
            grouping.group_subkey() == subkey,
            grouping.group_day() == day,
            Notification.seen == False,  # noqa: E712
        )
        .values(updated=utcnow(), seen=True)
    )

    await session.commit()
