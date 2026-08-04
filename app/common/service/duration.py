from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AnimeWatch, Anime, User
from sqlalchemy import select, update, func
from itertools import chain
from app import constants


def watch_duration(watch, anime):
    # Formula to calculate watch duration
    return func.coalesce(anime.duration, 0) * (
        func.coalesce(watch.episodes, 0)
        + func.coalesce(anime.episodes_total, 0)
        * func.coalesce(watch.rewatches, 0)
    )


def watch_stats(watch):
    def count_status(status):
        return func.count(watch.id).filter(watch.status == status)

    return {
        "duration": func.coalesce(func.sum(watch.duration), 0),
        "completed": count_status(constants.WATCH_COMPLETED),
        "watching": count_status(constants.WATCH_WATCHING),
        "planned": count_status(constants.WATCH_PLANNED),
        "on_hold": count_status(constants.WATCH_ON_HOLD),
        "dropped": count_status(constants.WATCH_DROPPED),
    }


def watch_stats_object(watch):
    return func.jsonb_build_object(
        *chain.from_iterable(watch_stats(watch).items()), type_=JSONB
    )


async def recalculate_watch_stats(session: AsyncSession, *filters):
    """Recalculate anime_stats in User from watch entries"""

    aggregate = (
        select(
            User.id.label("user_id"),
            watch_stats_object(AnimeWatch).label("anime_stats"),
        )
        .select_from(User)
        .outerjoin(AnimeWatch, AnimeWatch.user_id == User.id)
        .filter(*filters)
        .group_by(User.id)
        .subquery()
    )

    await session.execute(
        update(User)
        .values(anime_stats=aggregate.c.anime_stats)
        .filter(
            User.id == aggregate.c.user_id,
            User.anime_stats.is_distinct_from(aggregate.c.anime_stats),
        )
        .execution_options(synchronize_session=False)
    )

    await session.commit()


async def recalculate_watch_duration(session: AsyncSession, *filters):
    """Recalculate duration in AnimeWatch from current anime metadata"""

    duration = watch_duration(AnimeWatch, Anime)

    await session.execute(
        update(AnimeWatch)
        .values(duration=duration)
        .filter(
            Anime.id == AnimeWatch.anime_id,
            AnimeWatch.duration.is_distinct_from(duration),
        )
        .filter(*filters)
        .execution_options(synchronize_session=False)
    )

    await session.commit()
