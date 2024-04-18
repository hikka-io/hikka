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


def anime_schedule_filters(
    query: Select,
    args: AnimeScheduleArgs,
    request_user: User | None,
):
    if args.airing_season:
        season = args.airing_season[0]
        year = args.airing_season[1]

        query = query.filter(Anime.airing_seasons.op("?")(f"{season}_{year}"))

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

    if len(args.status) > 0:
        query = query.filter(Anime.status.in_(args.status))

    if len(args.rating) > 0:
        query = query.filter(Anime.rating.in_(args.rating))

    if request_user and args.only_watch:
        query = query.join(AnimeWatch).filter(
            AnimeWatch.anime_id == Anime.id,
            AnimeWatch.user == request_user,
        )

    return query


async def get_schedule_anime_count(
    session: AsyncSession, args: AnimeScheduleArgs, request_user: User | None
):
    return await session.scalar(
        anime_schedule_filters(
            select(func.count(AnimeSchedule.id)).join(AnimeSchedule.anime),
            args,
            request_user,
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
            select(AnimeSchedule).join(AnimeSchedule.anime),
            args,
            request_user,
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
