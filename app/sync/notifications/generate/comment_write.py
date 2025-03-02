from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification, User, Log
from app.comments.utils import path_to_uuid
from sqlalchemy import select
from app import constants
from .. import service
import re


async def generate_comment_write(session: AsyncSession, log: Log):
    # If there for some reason no comment - we should fail gracefully
    if not (comment := await service.get_comment(session, log.target_id)):
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

        # Continue if user wishes to ignore this type of notifications
        if notification_type in user.ignored_notifications:
            return

        # Do not create notification if we already did that
        if await service.get_notification(
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
                    "comment_reference": comment.reference,
                    "comment_depth": comment.depth,
                    "comment_text": comment.text,
                    "base_comment_reference": path_to_uuid(comment.path[0]),
                    "username": comment.author.username,
                    "avatar": comment.author.avatar,
                },
                "initiator_user_id": comment.author.id,
            }
        )

        session.add(notification)

    # Create notification for author of the edit
    if (
        comment.depth == 1
        and comment.content_type == constants.CONTENT_SYSTEM_EDIT
    ):
        notification_type = constants.NOTIFICATION_EDIT_COMMENT

        # If edit is gone for some reason, just continue on
        if not (edit := await service.get_edit(session, comment.content_id)):
            return

        if not edit.author:
            return

        # Stop if user wishes to ignore this type of notifications
        if notification_type in edit.author.ignored_notifications:
            return

        if edit.author == comment.author:
            return

        # Do not create notification if we already did that
        if await service.get_notification(
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
                    "comment_reference": comment.reference,
                    "comment_depth": comment.depth,
                    "comment_text": comment.text,
                    "base_comment_reference": path_to_uuid(comment.path[0]),
                    "username": comment.author.username,
                    "avatar": comment.author.avatar,
                },
                "initiator_user_id": comment.author.id,
            }
        )

        session.add(notification)

    # Create notification for author of the collection
    if (
        comment.depth == 1
        and comment.content_type == constants.CONTENT_COLLECTION
    ):
        notification_type = constants.NOTIFICATION_COLLECTION_COMMENT

        # If collection is gone for some reason, just continue on
        if not (
            collection := await service.get_collection(
                session, comment.content_id
            )
        ):
            return

        if not collection.author:
            return

        # Stop if user wishes to ignore this type of notifications
        if notification_type in collection.author.ignored_notifications:
            return

        if collection.author == comment.author:
            return

        # Do not create notification if we already did that
        if await service.get_notification(
            session,
            collection.author_id,
            log.id,
            notification_type,
        ):
            return

        # Fetch content in order to get slug
        await session.refresh(comment, attribute_names=["content"])

        notification = Notification(
            **{
                "notification_type": notification_type,
                "user_id": collection.author_id,
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
                    "username": comment.author.username,
                    "avatar": comment.author.avatar,
                },
                "initiator_user_id": comment.author.id,
            }
        )

        session.add(notification)

    # Create notification for author of the article
    if comment.depth == 1 and comment.content_type == constants.CONTENT_ARTICLE:
        notification_type = constants.NOTIFICATION_ARTICLE_COMMENT

        # If article is gone for some reason, just continue on
        if not (
            article := await service.get_article(session, comment.content_id)
        ):
            return

        if not article.author:
            return

        # Stop if user wishes to ignore this type of notifications
        if notification_type in article.author.ignored_notifications:
            return

        if article.author == comment.author:
            return

        # Do not create notification if we already did that
        if await service.get_notification(
            session,
            article.author_id,
            log.id,
            notification_type,
        ):
            return

        # Fetch content in order to get slug
        await session.refresh(comment, attribute_names=["content"])

        notification = Notification(
            **{
                "notification_type": notification_type,
                "user_id": article.author_id,
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
                    "username": comment.author.username,
                    "avatar": comment.author.avatar,
                },
                "initiator_user_id": comment.author.id,
            }
        )

        session.add(notification)

    # Create notification for the author replied comment
    if comment.depth > 1:
        notification_type = constants.NOTIFICATION_COMMENT_REPLY
        parent_path = comment.path[:-1]

        if not (
            parent_comment := await service.get_comment_by_path(
                session, parent_path
            )
        ):
            return

        # Stop if user wishes to ignore this type of notifications
        if notification_type in parent_comment.author.ignored_notifications:
            return

        # If user replied to his own comment, we should skip it
        if comment.author == parent_comment.author:
            return

        # Do not create notification if we already did that
        if await service.get_notification(
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
                    "comment_reference": comment.reference,
                    "comment_depth": comment.depth,
                    "comment_text": comment.text,
                    "base_comment_reference": path_to_uuid(comment.path[0]),
                    "username": comment.author.username,
                    "avatar": comment.author.avatar,
                },
                "initiator_user_id": comment.author.id,
            }
        )

        session.add(notification)
