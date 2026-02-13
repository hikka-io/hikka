from sqlalchemy import select, desc, func, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from app.utils import utcnow
from app import constants
import random

from app.models import (
    AnimeWatch,
    Follow,
    Anime,
    User,
)

from .schemas import (
    AnimeWatchSearchArgs,
    WatchArgs,
)

from app.service import (
    calculate_watch_duration,
    build_anime_order_by,
    anime_search_filter,
    get_anime_watch,
    anime_loadonly,
    create_log,
)


async def get_user_watch_stats(session: AsyncSession, user: User, status: str):
    return await session.scalar(
        select(func.count(AnimeWatch.id)).filter(
            # AnimeWatch.deleted == False,  # noqa: E712
            AnimeWatch.status == status,
            AnimeWatch.user == user,
        )
    )


async def get_user_watch_duration(session: AsyncSession, user: User):
    duration = await session.scalar(
        select(func.sum(AnimeWatch.duration)).filter(AnimeWatch.user == user)
    )

    return duration if duration else 0


async def generate_watch_stats(session: AsyncSession, user: User) -> User:
    completed = await get_user_watch_stats(
        session,
        user,
        constants.WATCH_COMPLETED,
    )

    watching = await get_user_watch_stats(
        session,
        user,
        constants.WATCH_WATCHING,
    )

    planned = await get_user_watch_stats(
        session,
        user,
        constants.WATCH_PLANNED,
    )

    on_hold = await get_user_watch_stats(
        session,
        user,
        constants.WATCH_ON_HOLD,
    )

    dropped = await get_user_watch_stats(
        session,
        user,
        constants.WATCH_DROPPED,
    )

    duration = await get_user_watch_duration(session, user)

    user.anime_stats = {
        "duration": duration,
        "completed": completed,
        "watching": watching,
        "planned": planned,
        "on_hold": on_hold,
        "dropped": dropped,
    }

    session.add(user)
    await session.commit()

    return user


async def save_watch(
    session: AsyncSession, anime: Anime, user: User, args: WatchArgs
):
    now = utcnow()
    log_type = constants.LOG_WATCH_UPDATE

    # Create watch record if missing
    if not (watch := await get_anime_watch(session, anime, user)):
        log_type = constants.LOG_WATCH_CREATE

        watch = AnimeWatch()
        watch.created = now
        watch.anime = anime
        watch.user = user

        session.add(watch)

        # Generally I think it's bad idea to modify user passed args
        # but this would allow us to keep existing logic so why not
        args.start_date = now

    # Same as with start_date we modify user passed args
    # in special case to simplify our lives
    if args.status == constants.WATCH_COMPLETED and watch.end_date is None:
        args.end_date = now

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

        await generate_watch_stats(session, user)

    return watch


async def delete_watch(session: AsyncSession, watch: AnimeWatch, user: User):
    await session.delete(watch)

    # Update user last list update
    user.updated = utcnow()
    session.add(user)

    await create_log(
        session,
        constants.LOG_WATCH_DELETE,
        user,
        watch.anime.id,
    )

    await generate_watch_stats(session, user)

    await session.commit()


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


async def get_user_watch_list(
    session: AsyncSession,
    search: AnimeWatchSearchArgs,
    user: User,
    limit: int,
    offset: int,
) -> ScalarResult[AnimeWatch]:
    query = select(AnimeWatch).filter(
        # AnimeWatch.deleted == False,  # noqa: E712
        AnimeWatch.user == user,
    )

    if search.watch_status:
        query = query.filter(AnimeWatch.status == search.watch_status)

    return await session.scalars(
        anime_search_filter(search, query.join(Anime), False)
        .order_by(*build_anime_order_by(search.sort))
        .options(anime_loadonly(joinedload(AnimeWatch.anime)))
        .limit(limit)
        .offset(offset)
    )


async def get_user_watch_list_count(
    session: AsyncSession, search: AnimeWatchSearchArgs, user: User
) -> int:
    query = select(func.count(AnimeWatch.id)).filter(
        # AnimeWatch.deleted == False,  # noqa: E712
        AnimeWatch.user == user,
    )

    if search.watch_status:
        query = query.filter(AnimeWatch.status == search.watch_status)

    query = anime_search_filter(search, query.join(Anime), False)

    return await session.scalar(query)


async def get_anime_watch_following_total(
    session: AsyncSession, user: User, anime: Anime
):
    return await session.scalar(
        select(func.count(User.id))
        .join(Follow, Follow.followed_user_id == User.id)
        .filter(Follow.user_id == user.id)
        .join(User.watch)
        .filter(AnimeWatch.anime == anime)
    )


async def get_anime_watch_following(
    session: AsyncSession, user: User, anime: Anime, limit: int, offset: int
):
    return await session.scalars(
        select(User)
        .join(Follow, Follow.followed_user_id == User.id)
        .filter(Follow.user_id == user.id)
        .join(User.watch)
        .filter(AnimeWatch.anime == anime)
        .options(contains_eager(User.watch))
        .order_by(desc(AnimeWatch.score), desc(AnimeWatch.updated))
        .limit(limit)
        .offset(offset)
    )
