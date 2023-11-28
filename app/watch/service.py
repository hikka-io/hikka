from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AnimeWatch, Anime, User
from sqlalchemy import select, desc, asc, func
from sqlalchemy.orm import selectinload
from .schemas import WatchArgs
from datetime import datetime
from app import constants

from app.service import (
    get_anime_watch,
    anime_loadonly,
)


# ToDo: rewrite this function?
async def save_watch(
    session: AsyncSession, anime: Anime, user: User, args: WatchArgs
):
    # Create watch record if missing
    if not (watch := await get_anime_watch(session, anime, user)):
        watch = AnimeWatch()
        watch.created = datetime.utcnow()
        watch.anime = anime
        watch.user = user

    # Set attributes from args to watch record
    for key, value in args.model_dump().items():
        setattr(watch, key, value)

    # Save watch record
    watch.updated = datetime.utcnow()

    session.add(watch)
    await session.commit()

    return watch


async def delete_watch(session: AsyncSession, watch: AnimeWatch):
    await session.delete(watch)
    await session.commit()


async def get_user_watch_list(
    session: AsyncSession,
    user: User,
    status: str | None,
    order: str,
    sort: str,
    limit: int,
    offset: int,
) -> list[AnimeWatch]:
    query = select(AnimeWatch).filter(AnimeWatch.user == user)
    query = query.filter(AnimeWatch.status == status) if status else query
    query = query.join(Anime)

    if order == constants.WATCH_ORDER_SCORE:
        query = query.order_by(
            desc(AnimeWatch.score)
            if sort == constants.SORT_DESC
            else asc(AnimeWatch.score)
        )

    if order == constants.WATCH_ORDER_EPISODES:
        query = query.order_by(
            desc(AnimeWatch.episodes)
            if sort == constants.SORT_DESC
            else asc(AnimeWatch.episodes)
        )

    if order == constants.WATCH_ORDER_MEDIA_TYPE:
        query = query.order_by(
            desc(Anime.media_type)
            if sort == constants.SORT_DESC
            else asc(Anime.media_type)
        )

    return await session.scalars(
        query.order_by(desc(Anime.content_id))
        .options(anime_loadonly(selectinload(AnimeWatch.anime)))
        .limit(limit)
        .offset(offset)
    )


async def get_user_watch_list_count(
    session: AsyncSession,
    user: User,
    status: str | None,
) -> int:
    query = select(func.count(AnimeWatch.id)).filter(AnimeWatch.user == user)
    query = query.filter(AnimeWatch.status == status) if status else query
    return await session.scalar(query)


async def get_user_watch_stats(session: AsyncSession, user: User, status: str):
    return await session.scalar(
        select(func.count(AnimeWatch.id)).filter(
            AnimeWatch.status == status,
            AnimeWatch.user == user,
        )
    )
