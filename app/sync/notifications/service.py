from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app import constants
from uuid import UUID

from app.models import (
    Notification,
    Collection,
    AnimeWatch,
    Comment,
    Anime,
    Edit,
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


async def get_collection(session, content_id):
    return await session.scalar(
        select(Collection).filter(
            Collection.id == content_id,
            Collection.deleted == False,  # noqa: E712
        )
    )


async def get_anime(session, anime_id):
    return await session.scalar(select(Anime).filter(Anime.id == anime_id))


async def get_anime_watch_user_ids(session: AsyncSession, anime: Anime):
    return await session.scalars(
        select(AnimeWatch.user_id).filter(
            AnimeWatch.anime == anime,
            AnimeWatch.status.in_(
                [constants.WATCH_PLANNED, constants.WATCH_WATCHING]
            ),
        )
    )
