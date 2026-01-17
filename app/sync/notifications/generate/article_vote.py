from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, Log
from datetime import timedelta
from app import constants
from .. import service


# TODO: we should probably merge this and collections vote logic somehow
async def generate_article_vote(session: AsyncSession, log: Log):
    notification_type = constants.NOTIFICATION_ARTICLE_VOTE

    # If there for some reason no article - we should fail gracefully
    if not (article := await service.get_article(session, log.target_id)):
        return

    # Stop if user wishes to ignore this type of notifications
    if notification_type in article.author.ignored_notifications:
        return

    # Stop if user who set the vote ceised to exist
    if not (user := await service.get_user_by_id(session, log.user_id)):
        return

    # Skip if user voted for own article
    if log.user_id == article.author_id:
        return

    # Skip removal of score
    if log.data["user_score"] == 0:
        return

    # Do not create notification if we already did that
    if await service.get_notification(
        session, article.author_id, log.id, notification_type
    ):
        return

    # Prevent article vote notifications spam
    if await service.count_notifications_spam(
        session,
        article.author_id,
        user.username,
        notification_type,
        timedelta(hours=6),
        article.reference,
    ):
        return

    user_score = log.data["user_score"]

    notification = Notification(
        **{
            "notification_type": notification_type,
            "user_id": article.author_id,
            "created": log.created,
            "updated": log.created,
            "log_id": log.id,
            "seen": False,
            "data": {
                "slug": article.reference,
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
