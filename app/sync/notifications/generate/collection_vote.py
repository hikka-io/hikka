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

    # Stop if user who set the vote ceised to exist
    if not (user := await service.get_user_by_id(session, log.user_id)):
        return

    # Skip removal of score
    if log.data["user_score"] == 0:
        return

    user_score = log.data["user_score"]

    # Owner and co-authors all get notified, except the voter. NOTE: the
    # check below is a continue, not a return, otherwise the first skipped
    # recipient would cut the rest of them off
    for recipient in await service.get_collection_recipients(
        session, collection, log.id, notification_type, log.user_id
    ):
        # Prevent collection vote notifications spam
        if await service.count_notifications_spam(
            session,
            recipient.id,
            user.username,
            notification_type,
            timedelta(hours=6),
            collection.reference,
        ):
            continue

        notification = Notification(
            **{
                "notification_type": notification_type,
                "user_id": recipient.id,
                "created": log.created,
                "updated": log.created,
                "log_id": log.id,
                "seen": False,
                "data": {
                    "slug": collection.reference,
                    "user_score": user_score,
                    "old_score": log.data["old_score"],
                    "new_score": log.data["new_score"],
                    "username": user.username if user_score > 0 else None,
                    "avatar": user.avatar if user_score > 0 else None,
                },
                "initiator_user_id": user.id if user_score > 0 else None,
            }
        )

        session.add(notification)
