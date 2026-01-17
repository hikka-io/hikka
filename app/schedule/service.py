from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.sql.selectable import Select
from sqlalchemy import select, asc, func
from .schemas import AnimeScheduleArgs
from app.service import anime_loadonly
from sqlalchemy.orm import joinedload
from datetime import timedelta
from app.utils import utcnow

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

    # TODO: do we need this?
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
        ).filter(
            Anime.nsfw == False,  # noqa: E712
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
        .filter(Anime.nsfw == False)  # noqa: E712
        .options(
            anime_loadonly(joinedload(AnimeSchedule.anime)).joinedload(
                Anime.watch
            ),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        )
        .order_by(asc(AnimeSchedule.airing_at), AnimeSchedule.id)
        .limit(limit)
        .offset(offset)
    )
