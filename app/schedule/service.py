from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql.selectable import Select
from sqlalchemy import select, asc, func
from .schemas import AnimeScheduleArgs
from app.service import anime_loadonly
from sqlalchemy.orm import joinedload
from datetime import timedelta

from app.utils import (
    utcfromtimestamp,
    utcnow,
)

from app.models import (
    AnimeSchedule,
    AnimeWatch,
    Anime,
    User,
)


def anime_schedule_filters(query: Select, args: AnimeScheduleArgs):
    if args.airing_season:
        query = query.filter(
            Anime.season == args.airing_season[0],
            Anime.year == args.airing_season[1],
        )

    if args.airing_range:
        airing_start = (
            utcfromtimestamp(args.airing_range[0])
            if args.airing_range[0]
            else None
        )

        airing_end = (
            utcfromtimestamp(args.airing_range[1])
            if args.airing_range[1]
            else None
        )

        if airing_start:
            query = query.filter(AnimeSchedule.airing_at >= airing_start)

        if airing_end:
            query = query.filter(AnimeSchedule.airing_at <= airing_end)

    else:
        query = query.filter(
            AnimeSchedule.airing_at >= utcnow() - timedelta(hours=6)
        )

    if args.status:
        query = query.filter(Anime.status == args.status)

    if len(args.rating) > 0:
        query = query.filter(Anime.rating.in_(args.rating))

    return query


async def get_schedule_anime_count(
    session: AsyncSession, args: AnimeScheduleArgs
):
    return await session.scalar(
        anime_schedule_filters(
            select(func.count(AnimeSchedule.id)).join(AnimeSchedule.anime), args
        )
    )


async def get_schedule_anime(
    session: AsyncSession,
    args: AnimeScheduleArgs,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        anime_schedule_filters(
            select(AnimeSchedule).join(AnimeSchedule.anime), args
        )
        .options(
            anime_loadonly(joinedload(AnimeSchedule.anime)).joinedload(
                Anime.watch
            ),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        )
        .order_by(asc(AnimeSchedule.airing_at))
        .limit(limit)
        .offset(offset)
    )
