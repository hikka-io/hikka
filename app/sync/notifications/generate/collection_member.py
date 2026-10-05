from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, Log
from datetime import timedelta
from uuid import UUID
from .. import service


async def generate_collection_member_notification(
    session: AsyncSession,
    log: Log,
    notification_type: str,
    spam_delta: timedelta | None = None,
):
    """
    Notify the member a collection log is about (log.data["user_id"])

    Shared by invites and ownership offers, which only differ in type and
    in whether repeated notifications are throttled.
    """

    # If there for some reason no collection - we should fail gracefully
    if not (collection := await service.get_collection(session, log.target_id)):
        return

    # Stop if user who acted on the collection ceised to exist
    if not (user := await service.get_user_by_id(session, log.user_id)):
        return

    if not (
        member_user := await service.get_user_by_id(
            session, UUID(log.data["user_id"])
        )
    ):
        return

    # Stop if user wishes to ignore this type of notifications
    if notification_type in member_user.ignored_notifications:
        return

    # Do not create notification if we already did that
    if await service.get_notification(
        session, member_user.id, log.id, notification_type
    ):
        return

    # Prevent notifications spam
    if spam_delta and await service.count_notifications_spam(
        session,
        member_user.id,
        user.username,
        notification_type,
        spam_delta,
        collection.reference,
    ):
        return

    notification = Notification(
        **{
            "notification_type": notification_type,
            "user_id": member_user.id,
            "created": log.created,
            "updated": log.created,
            "log_id": log.id,
            "seen": False,
            "data": {
                "slug": collection.reference,
                "title": collection.title,
                "username": user.username,
                "avatar": user.avatar,
            },
            "initiator_user_id": user.id,
        }
    )

    session.add(notification)
