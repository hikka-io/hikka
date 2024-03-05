from sqlalchemy.ext.asyncio import AsyncSession
from app.comments.utils import path_to_uuid
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
    user_id: UUID,
    log_id: UUID,
    notification_type: str | None = None,
):
    query = select(Notification).filter(
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


async def generate_comment_vote(session: AsyncSession, log: Log):
    notification_type = constants.NOTIFICATION_COMMENT_VOTE

    # If there for some reason no comment - we should fail gracefully
    if not (comment := await get_comment(session, log.target_id)):
        return

    # Skip if user voted for own comment
    if log.user_id == comment.author_id:
        return

    # Skip removal of score
    if log.data["user_score"] == 0:
        return

    # Do not create notification if we already did that
    if await get_notification(
        session,
        comment.author_id,
        log.id,
        notification_type,
    ):
        return

    # Fetch content in order to get slug
    await session.refresh(comment, attribute_names=["content"])

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
            },
        }
    )

    session.add(notification)


async def generate_comment_write(session: AsyncSession, log: Log):
    # If there for some reason no comment - we should fail gracefully
    if not (comment := await get_comment(session, log.target_id)):
        return

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
            user.id,
            log.id,
            notification_type,
        ):
            continue

        # Fetch content in order to get slug
        await session.refresh(comment, attribute_names=["content"])

        notification = Notification(
            **{
                "notification_type": notification_type,
                "created": log.created,
                "updated": log.created,
                "user_id": user.id,
                "log_id": log.id,
                "seen": False,
                "data": {
                    "slug": comment.content.slug,
                    "content_type": comment.content_type,
                    "comment_author": comment.author.username,
                    "comment_reference": comment.reference,
                    "comment_depth": comment.depth,
                    "comment_text": comment.text,
                    "base_comment_reference": path_to_uuid(comment.path[0]),
                },
            }
        )

        session.add(notification)

    # Create notification for author of the edit
    if (
        comment.depth == 1
        and comment.content_type == constants.CONTENT_SYSTEM_EDIT
    ):
        # If edit is gone for some reason, just continue on
        if not (edit := await get_edit(session, comment.content_id)):
            return

        if not edit.author:
            return

        if edit.author == comment.author:
            return

        notification_type = constants.NOTIFICATION_EDIT_COMMENT

        # Do not create notification if we already did that
        if await get_notification(
            session,
            edit.author_id,
            log.id,
            notification_type,
        ):
            return

        # Fetch content in order to get slug
        await session.refresh(comment, attribute_names=["content"])

        notification = Notification(
            **{
                "notification_type": notification_type,
                "user_id": edit.author_id,
                "created": log.created,
                "updated": log.created,
                "log_id": log.id,
                "seen": False,
                "data": {
                    "slug": comment.content.slug,
                    "content_type": comment.content_type,
                    "comment_author": comment.author.username,
                    "comment_reference": comment.reference,
                    "comment_depth": comment.depth,
                    "comment_text": comment.text,
                    "base_comment_reference": path_to_uuid(comment.path[0]),
                },
            }
        )

        session.add(notification)

    # Create notification for the author replied comment
    if comment.depth > 1:
        parent_path = comment.path[:-1]
        if not (
            parent_comment := await get_comment_by_path(session, parent_path)
        ):
            return

        # If user replied to his own comment, we should skip it
        if comment.author == parent_comment.author:
            return

        notification_type = constants.NOTIFICATION_COMMENT_REPLY

        # Do not create notification if we already did that
        if await get_notification(
            session,
            comment.author_id,
            log.id,
            notification_type,
        ):
            return

        # Fetch content in order to get slug
        await session.refresh(comment, attribute_names=["content"])

        notification = Notification(
            **{
                "notification_type": notification_type,
                "user_id": parent_comment.author.id,
                "created": log.created,
                "updated": log.created,
                "log_id": log.id,
                "seen": False,
                "data": {
                    "slug": comment.content.slug,
                    "content_type": comment.content_type,
                    "comment_author": comment.author.username,
                    "comment_reference": comment.reference,
                    "comment_depth": comment.depth,
                    "comment_text": comment.text,
                    "base_comment_reference": path_to_uuid(comment.path[0]),
                },
            }
        )

        session.add(notification)


async def generate_edit_accept(session: AsyncSession, log: Log):
    # If edit is gone for some reason, just continue on
    if not (edit := await get_edit(session, log.target_id)):
        return

    if not edit.author:
        return

    if edit.author_id == edit.moderator_id:
        return

    notification_type = constants.NOTIFICATION_EDIT_ACCEPTED

    # Do not create notification if we already did that
    if await get_notification(
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
                "edit_id": edit.edit_id,
            },
        }
    )

    session.add(notification)


async def generate_edit_deny(session: AsyncSession, log: Log):
    # If edit is gone for some reason, just continue on
    if not (edit := await get_edit(session, log.target_id)):
        return

    if not edit.author:
        return

    if edit.author_id == edit.moderator_id:
        return

    notification_type = constants.NOTIFICATION_EDIT_DENIED

    # Do not create notification if we already did that
    if await get_notification(
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
                "edit_id": edit.edit_id,
            },
        }
    )

    session.add(notification)


async def generate_edit_update(session: AsyncSession, log: Log):
    # If edit is gone for some reason, just continue on
    if not (edit := await get_edit(session, log.target_id)):
        return

    if not edit.author:
        return

    # Make sure edit is updated by someone else
    if edit.author_id == log.user_id:
        return

    notification_type = constants.NOTIFICATION_EDIT_UPDATED

    # Do not create notification if we already did that
    if await get_notification(
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
                "updated_edit": log.data["updated_edit"],
                "old_edit": log.data["old_edit"],
                "username": log.user.username,
                "edit_id": edit.edit_id,
            },
        }
    )

    session.add(notification)


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
                    constants.LOG_COMMENT_VOTE,
                    constants.LOG_EDIT_ACCEPT,
                    constants.LOG_EDIT_DENY,
                    constants.LOG_EDIT_UPDATE,  # ToDo
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    for log in logs:
        # We set timestamp here because after thay it won't be set due to continue
        system_timestamp.timestamp = log.created

        if log.log_type == constants.LOG_COMMENT_VOTE:
            await generate_comment_vote(session, log)

        if log.log_type == constants.LOG_COMMENT_WRITE:
            await generate_comment_write(session, log)

        # Create notification for edit author if edit was accepted
        if log.log_type == constants.LOG_EDIT_ACCEPT:
            await generate_edit_accept(session, log)

        # Create notification for edit author if edit was denied
        if log.log_type == constants.LOG_EDIT_DENY:
            await generate_edit_deny(session, log)

        # Create notification for edit author if edit was denied
        if log.log_type == constants.LOG_EDIT_UPDATE:
            await generate_edit_update(session, log)

    session.add(system_timestamp)
    await session.commit()


async def update_notifications():
    """Generate users notifications from logs"""

    async with sessionmanager.session() as session:
        await generate_notifications(session)
