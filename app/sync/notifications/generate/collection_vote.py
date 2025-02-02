from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, Log
from datetime import timedelta
from app import constants
from .. import service


async def generate_collection_vote(session: AsyncSession, log: Log):
    notification_type = constants.NOTIFICATION_COLLECTION_VOTE

    # If there for some reason no collection - we should fail gracefully
    if not (collection := await service.get_collection(session, log.target_id)):
        return

    # Stop if user wishes to ignore this type of notifications
    if notification_type in collection.author.ignored_notifications:
        return

    # Stop if user who set the vote ceised to exist
    if not (user := await service.get_user_by_id(session, log.user_id)):
        return

    # Skip if user voted for own collection
    if log.user_id == collection.author_id:
        return

    # Skip removal of score
    if log.data["user_score"] == 0:
        return

    # Do not create notification if we already did that
    if await service.get_notification(
        session, collection.author_id, log.id, notification_type
    ):
        return

    # Prevent collection vote notifications spam
    if await service.count_notifications_spam(
        session,
        collection.author_id,
        user.username,
        notification_type,
        timedelta(hours=6),
        collection.reference,
    ):
        return

    notification = Notification(
        **{
            "notification_type": notification_type,
            "user_id": collection.author_id,
            "created": log.created,
            "updated": log.created,
            "log_id": log.id,
            "seen": False,
            "data": {
                "slug": collection.reference,
                "user_score": log.data["user_score"],
                "old_score": log.data["old_score"],
                "new_score": log.data["new_score"],
                "username": user.username,
                "avatar": user.avatar,
            },
            "initiator_user_id": user.id,
        }
    )

    session.add(notification)
