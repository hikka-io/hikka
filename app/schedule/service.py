from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy import select, asc, func
from datetime import datetime, timedelta
from app.service import anime_loadonly
from sqlalchemy.orm import joinedload

from app.models import (
    AnimeSchedule,
    AnimeWatch,
    Anime,
    User,
)


async def get_schedule_anime_count(session: AsyncSession):
    return await session.scalar(
        select(func.count(AnimeSchedule.id)).filter(
            AnimeSchedule.airing_at >= datetime.utcnow() - timedelta(hours=6)
        )
    )


async def get_schedule_anime(
    session: AsyncSession, request_user: User | None, limit: int, offset: int
):
    return await session.scalars(
        select(AnimeSchedule)
        .filter(
            AnimeSchedule.airing_at >= datetime.utcnow() - timedelta(hours=6)
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
        # .options(joinedload(AnimeSchedule.anime))
        .order_by(asc(AnimeSchedule.airing_at))
        .limit(limit)
        .offset(offset)
    )
