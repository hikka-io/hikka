from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AnimeWatch, Anime, User
from sqlalchemy import select, desc, asc, func
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import selectinload
from datetime import datetime
from app import constants
import random

from .schemas import (
    AnimeWatchSearchArgs,
    WatchArgs,
)

from app.service import (
    calculate_watch_duration,
    anime_search_filter,
    get_anime_watch,
    anime_loadonly,
    create_log,
)


# ToDo: rewrite this function?
async def save_watch(
    session: AsyncSession, anime: Anime, user: User, args: WatchArgs
):
    now = datetime.utcnow()
    log_type = constants.LOG_WATCH_UPDATE

    # Create watch record if missing
    if not (watch := await get_anime_watch(session, anime, user)):
        log_type = constants.LOG_WATCH_CREATE
        watch = AnimeWatch()
        watch.created = now
        watch.anime = anime
        watch.user = user

    log_before = {}
    log_after = {}

    # Set attributes from args to watch record
    for key, new_value in args.model_dump().items():
        # Here we add changes to log's before/after dicts only if there are changes
        old_value = getattr(watch, key)
        if old_value != new_value:
            log_before[key] = old_value
            setattr(watch, key, new_value)
            log_after[key] = new_value

    # Calculate duration and update updated field
    watch.duration = calculate_watch_duration(watch)
    watch.updated = now

    # Update user last list update
    user.updated = now
    session.add_all([watch, user])

    await session.commit()

    if log_before != {} and log_after != {} and log_before != log_after:
        await create_log(
            session,
            log_type,
            user,
            anime.id,
            {
                "before": log_before,
                "after": log_after,
            },
        )

    return watch


async def delete_watch(session: AsyncSession, watch: AnimeWatch, user: User):
    await session.delete(watch)

    # Update user last list update
    user.updated = datetime.utcnow()
    session.add(user)

    await create_log(
        session,
        constants.LOG_WATCH_DELETE,
        user,
        watch.anime.id,
    )

    await session.commit()


async def get_user_watch_list_legacy(
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


async def get_user_watch_list_count_legacy(
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


async def random_watch(session: AsyncSession, user: User, status: str | None):
    anime_ids = await session.scalars(
        select(AnimeWatch.anime_id).filter(
            AnimeWatch.user == user, AnimeWatch.status == status
        )
    )

    anime = await session.scalar(
        select(Anime).filter(Anime.id == random.choice(anime_ids.all()))
    )

    return anime


async def get_user_watch_duration(session: AsyncSession, user: User):
    duration = await session.scalar(
        select(func.sum(AnimeWatch.duration)).filter(AnimeWatch.user == user)
    )

    return duration if duration else 0


async def get_user_watch_list(
    session: AsyncSession,
    search: AnimeWatchSearchArgs,
    user: User,
    limit: int,
    offset: int,
) -> list[AnimeWatch]:
    order_mapping = {
        "watch_episodes": AnimeWatch.episodes,
        "watch_created": AnimeWatch.created,
        "watch_score": AnimeWatch.score,
        "media_type": Anime.media_type,
        "start_date": Anime.start_date,
        "scored_by": Anime.scored_by,
        "score": Anime.score,
    }

    order_by = [
        (
            desc(order_mapping[field])
            if order == "desc"
            else asc(order_mapping[field])
        )
        for field, order in (entry.split(":") for entry in search.sort)
    ] + [desc(Anime.content_id)]

    query = select(AnimeWatch).filter(AnimeWatch.user == user)

    if search.watch_status:
        query = query.filter(AnimeWatch.status == search.watch_status)

    return await session.scalars(
        anime_search_filter(search, query.join(Anime), False)
        .order_by(*order_by)
        .options(anime_loadonly(selectinload(AnimeWatch.anime)))
        .limit(limit)
        .offset(offset)
    )


async def get_user_watch_list_count(
    session: AsyncSession, search: AnimeWatchSearchArgs, user: User
) -> int:
    query = select(func.count(AnimeWatch.id)).filter(AnimeWatch.user == user)

    if search.watch_status:
        query = query.filter(AnimeWatch.status == search.watch_status)

    query = anime_search_filter(search, query.join(Anime), False)

    return await session.scalar(query)
