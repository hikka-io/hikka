from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from app.database import sessionmanager
from datetime import datetime
from app import constants
from uuid import UUID
import re

from app.models import (
    SystemTimestamp,
    Notification,
    Comment,
    Edit,
    User,
    Log,
)


async def get_notification(
    session: AsyncSession,
    target_id: UUID,
    user_id: UUID,
    log_id: UUID,
    notification_type: str | None = None,
):
    query = select(Notification).filter(
        Notification.target_id == target_id,
        Notification.user_id == user_id,
        Notification.log_id == log_id,
    )

    if notification_type:
        query = query.filter(
            Notification.notification_type == notification_type,
        )

    return await session.scalar(query.order_by(desc(Notification.created)))


async def get_comment(session, comment_id, hidden=False):
    return await session.scalar(
        select(Comment).filter(
            Comment.id == comment_id,
            Comment.hidden == hidden,  # noqa: E712
        )
    )


async def get_comment_by_path(session, path, hidden=False):
    return await session.scalar(
        select(Comment).filter(
            Comment.path == path,
            Comment.hidden == hidden,  # noqa: E712
        )
    )


async def get_edit(session, content_id):
    return await session.scalar(select(Edit).filter(Edit.id == content_id))


# I really how we will split this function into many one day
async def generate_notifications(session: AsyncSession):
    # Get system timestamp for latest history update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(
                SystemTimestamp.name == "notifications"
            )
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "notifications",
            }
        )

    # Get new logs that were created since last update
    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_COMMENT_WRITE,
                    constants.LOG_EDIT_ACCEPT,
                    constants.LOG_EDIT_DENY,
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    for log in logs:
        if log.log_type == constants.LOG_COMMENT_WRITE:
            # If there for some reason no comment - we should fail gracefully
            if not (comment := await get_comment(session, log.target_id)):
                continue

            # Get tagged usernames here
            usernames = re.findall(r"@([a-zA-Z0-9_]+)", comment.text)
            usernames = list(set(usernames))[:10]

            users = await session.scalars(
                select(User).filter(User.username.in_(usernames))
            )

            notification_type = constants.NOTIFICATION_COMMENT_TAG

            for user in users:
                if user == comment.author:
                    continue

                # Do not create notification if we already did that
                if await get_notification(
                    session,
                    comment.id,
                    user.id,
                    log.id,
                    notification_type,
                ):
                    continue

                notification = Notification(
                    **{
                        "notification_type": notification_type,
                        "target_id": comment.id,
                        "created": log.created,
                        "updated": log.created,
                        "user_id": user.id,
                        "log_id": log.id,
                        "seen": False,
                    }
                )

                session.add(notification)

            await session.commit()

            # Create notification for author of the edit
            if (
                comment.depth == 1
                and comment.content_type == constants.CONTENT_SYSTEM_EDIT
            ):
                # If edit is gone for some reason, just continue on
                if not (edit := await get_edit(session, comment.content_id)):
                    continue

                if not edit.author:
                    continue

                if edit.author == comment.author:
                    continue

                notification_type = constants.NOTIFICATION_EDIT_COMMENT

                # Do not create notification if we already did that
                if await get_notification(
                    session,
                    edit.id,
                    edit.author_id,
                    log.id,
                    notification_type,
                ):
                    continue

                notification = Notification(
                    **{
                        "notification_type": notification_type,
                        "user_id": edit.author_id,
                        "created": log.created,
                        "updated": log.created,
                        "target_id": edit.id,
                        "log_id": log.id,
                        "seen": False,
                    }
                )

                session.add(notification)
                await session.commit()

            # Create notification for the author replied comment
            if comment.depth > 1:
                parent_path = comment.path[:-1]
                if not (
                    parent_comment := await get_comment_by_path(
                        session, parent_path
                    )
                ):
                    continue

                # If user replied to his own comment, we should skip it
                if comment.author == parent_comment.author:
                    continue

                notification_type = constants.NOTIFICATION_COMMENT_REPLY

                # Do not create notification if we already did that
                if await get_notification(
                    session,
                    parent_comment.id,
                    parent_comment.author.id,
                    log.id,
                    notification_type,
                ):
                    continue

                notification = Notification(
                    **{
                        "notification_type": notification_type,
                        "user_id": parent_comment.author.id,
                        "target_id": parent_comment.id,
                        "created": log.created,
                        "updated": log.created,
                        "log_id": log.id,
                        "seen": False,
                    }
                )

                session.add(notification)
                await session.commit()

        # Create notification for edit author if edit was accepted
        if log.log_type == constants.LOG_EDIT_ACCEPT:
            # If edit is gone for some reason, just continue on
            if not (edit := await get_edit(session, log.target_id)):
                continue

            if not edit.author:
                continue

            if edit.author_id == edit.moderator_id:
                continue

            notification_type = constants.NOTIFICATION_EDIT_ACCEPTED

            # Do not create notification if we already did that
            if await get_notification(
                session,
                edit.id,
                edit.author_id,
                log.id,
                notification_type,
            ):
                continue

            notification = Notification(
                **{
                    "notification_type": notification_type,
                    "user_id": edit.author_id,
                    "created": log.created,
                    "updated": log.created,
                    "target_id": edit.id,
                    "log_id": log.id,
                    "seen": False,
                }
            )

            session.add(notification)
            await session.commit()

        # Create notification for edit author if edit was denied
        if log.log_type == constants.LOG_EDIT_DENY:
            # If edit is gone for some reason, just continue on
            if not (edit := await get_edit(session, log.target_id)):
                continue

            if not edit.author:
                continue

            if edit.author_id == edit.moderator_id:
                continue

            notification_type = constants.NOTIFICATION_EDIT_DENIED

            # Do not create notification if we already did that
            if await get_notification(
                session,
                edit.id,
                edit.author_id,
                log.id,
                notification_type,
            ):
                continue

            notification = Notification(
                **{
                    "notification_type": notification_type,
                    "user_id": edit.author_id,
                    "created": log.created,
                    "updated": log.created,
                    "target_id": edit.id,
                    "log_id": log.id,
                    "seen": False,
                }
            )

            session.add(notification)
            await session.commit()

        system_timestamp.timestamp = log.created

    session.add(system_timestamp)
    await session.commit()


async def update_notifications():
    """Generate users notifications from logs"""

    async with sessionmanager.session() as session:
        await generate_notifications(session)
