from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, AnimeWatch, Anime
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc
from sqlalchemy import func
from typing import Union


async def get_user_watch(
    session: AsyncSession,
    user: User,
    status: Union[str, None],
    limit: int,
    offset: int,
):
    query = select(AnimeWatch).filter_by(user=user)
    query = query.filter_by(status=status) if status else query

    return await session.scalars(
        query.order_by(desc(AnimeWatch.updated))
        .options(
            selectinload(AnimeWatch.anime).load_only(
                Anime.scored_by,
                Anime.title_ja,
                Anime.title_en,
                Anime.title_ua,
                Anime.episodes,
                Anime.status,
                Anime.score,
            )
        )
        .limit(limit)
        .offset(offset)
    )


async def get_user_watch_count(
    session: AsyncSession,
    user: User,
    status: Union[str, None],
):
    query = select(func.count(AnimeWatch.id)).filter_by(user=user)
    query = query.filter_by(status=status) if status else query
    return await session.scalar(query)
