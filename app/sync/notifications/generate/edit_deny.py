from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, Log
from app import constants
from .. import service


async def generate_edit_deny(session: AsyncSession, log: Log):
    # If edit is gone for some reason, just continue on
    if not (edit := await service.get_edit(session, log.target_id)):
        return

    if not edit.author:
        return

    if edit.author_id == edit.moderator_id:
        return

    notification_type = constants.NOTIFICATION_EDIT_DENIED

    # Do not create notification if we already did that
    if await service.get_notification(
        session,
        edit.author_id,
        log.id,
        notification_type,
    ):
        return

    await session.refresh(log, attribute_names=["user"])

    notification = Notification(
        **{
            "notification_type": notification_type,
            "user_id": edit.author_id,
            "created": log.created,
            "updated": log.created,
            "log_id": log.id,
            "seen": False,
            "data": {
                "description": edit.description,
                "username": log.user.username,
                "avatar": log.user.avatar,
                "edit_id": edit.edit_id,
            },
        }
    )

    session.add(notification)
