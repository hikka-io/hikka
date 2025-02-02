from sqlalchemy.ext.asyncio import AsyncSession
from app.comments.utils import path_to_uuid
from app.models import Notification, Log
from datetime import timedelta
from app import constants
from .. import service


async def generate_comment_vote(session: AsyncSession, log: Log):
    notification_type = constants.NOTIFICATION_COMMENT_VOTE

    # If there for some reason no comment - we should fail gracefully
    if not (comment := await service.get_comment(session, log.target_id)):
        return

    # Stop if user wishes to ignore this type of notifications
    if notification_type in comment.author.ignored_notifications:
        return

    # Stop if user who set the vote ceised to exist
    if not (user := await service.get_user_by_id(session, log.user_id)):
        return

    # Skip if user voted for own comment
    if log.user_id == comment.author_id:
        return

    # Skip removal of score
    if log.data["user_score"] == 0:
        return

    # Do not create notification if we already did that
    if await service.get_notification(
        session, comment.author_id, log.id, notification_type
    ):
        return

    # Fetch content in order to get slug
    await session.refresh(comment, attribute_names=["content"])

    # Prevent comment vote notifications spam
    if await service.count_notifications_spam(
        session,
        comment.author_id,
        user.username,
        notification_type,
        timedelta(hours=6),
        comment.content.slug,
        comment.content_type,
    ):
        return

    notification = Notification(
        **{
            "notification_type": notification_type,
            "user_id": comment.author_id,
            "created": log.created,
            "updated": log.created,
            "log_id": log.id,
            "seen": False,
            "data": {
                "slug": comment.content.slug,
                "content_type": comment.content_type,
                "comment_reference": comment.reference,
                "comment_depth": comment.depth,
                "comment_text": comment.text,
                "base_comment_reference": path_to_uuid(comment.path[0]),
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
