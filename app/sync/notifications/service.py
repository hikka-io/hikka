from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from datetime import timedelta
from app.utils import utcnow
from app import constants
from uuid import UUID

from app.models import (
    Notification,
    Collection,
    AnimeWatch,
    Comment,
    Anime,
    Edit,
    User,
)


async def get_user_by_id(session: AsyncSession, user_id: UUID):
    return await session.scalar(select(User).filter(User.id == user_id))


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


async def count_notifications_spam(
    session: AsyncSession,
    user_id: User,
    username: str,
    notification_type: str,
    delta: timedelta,
    slug: str = None,
    content_type: str = None,
):
    query = select(func.count(Notification.id)).filter(
        Notification.notification_type == notification_type,
        Notification.data.op("->>")("username") == username,
        Notification.created > utcnow() - delta,
        Notification.user_id == user_id,
    )

    if slug is not None:
        query = query.filter(Notification.data.op("->>")("slug") == slug)

    if content_type is not None:
        query = query.filter(
            Notification.data.op("->>")("content_type") == content_type
        )

    return await session.scalar(query)


async def get_comment(session, comment_id, hidden=False):
    return await session.scalar(
        select(Comment).filter(
            Comment.id == comment_id,
            Comment.hidden == hidden,  # noqa: E712
            Comment.deleted == False,  # noqa: E712
        )
    )


async def get_comment_by_path(session, path, hidden=False):
    return await session.scalar(
        select(Comment).filter(
            Comment.path == path,
            Comment.hidden == hidden,  # noqa: E712
            Comment.deleted == False,  # noqa: E712
        )
    )


async def get_edit(session, content_id):
    return await session.scalar(select(Edit).filter(Edit.id == content_id))


async def get_collection(session, content_id):
    return await session.scalar(
        select(Collection)
        .filter(
            Collection.id == content_id,
            Collection.deleted == False,  # noqa: E712
        )
        .options(joinedload(Collection.author))
    )


async def get_anime(session, anime_id):
    return await session.scalar(
        select(Anime).filter(
            Anime.id == anime_id,
            Anime.deleted == False,  # noqa: E712
        )
    )


async def get_anime_watch(session: AsyncSession, anime: Anime):
    return await session.scalars(
        select(AnimeWatch)
        .filter(
            AnimeWatch.deleted == False,  # noqa: E712
            AnimeWatch.anime == anime,
            AnimeWatch.status.in_(
                [
                    constants.WATCH_PLANNED,
                    constants.WATCH_WATCHING,
                    constants.WATCH_ON_HOLD,
                ]
            ),
        )
        .options(joinedload(AnimeWatch.user))
    )
