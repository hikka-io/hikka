from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, Log
from datetime import timedelta
from app import constants
from .. import service


async def generate_follow(session: AsyncSession, log: Log):
    notification_type = constants.NOTIFICATION_FOLLOW

    if not (user := await service.get_user_by_id(session, log.user_id)):
        return

    # Do not create notification if we already did that
    if await service.get_notification(
        session,
        log.target_id,
        log.id,
        notification_type,
    ):
        return

    # Prevent follow notifications spam
    if await service.count_notifications_spam(
        session,
        log.target_id,
        user.username,
        notification_type,
        timedelta(hours=6),
    ):
        return

    notification = Notification(
        **{
            "notification_type": notification_type,
            "user_id": log.target_id,
            "created": log.created,
            "updated": log.created,
            "log_id": log.id,
            "seen": False,
            "data": {
                "username": user.username,
                "avatar": user.avatar,
            },
        }
    )

    session.add(notification)
