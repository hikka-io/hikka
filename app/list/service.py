from app.models import User, Anime, AnimeWatch, AnimeFavourite
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc
from sqlalchemy import func
from typing import Union


def anime_selectinload():
    return selectinload(AnimeWatch.anime).load_only(
        Anime.media_type,
        Anime.scored_by,
        Anime.title_ja,
        Anime.title_en,
        Anime.title_ua,
        Anime.episodes,
        Anime.status,
        Anime.score,
        Anime.slug,
    )


async def get_user_watch(
    session: AsyncSession,
    user: User,
    status: Union[str, None],
    limit: int,
    offset: int,
) -> list[AnimeWatch]:
    query = select(AnimeWatch).filter_by(user=user)
    query = query.filter_by(status=status) if status else query

    return await session.scalars(
        query.order_by(desc(AnimeWatch.updated))
        .options(anime_selectinload())
        .limit(limit)
        .offset(offset)
    )


async def get_user_watch_count(
    session: AsyncSession,
    user: User,
    status: Union[str, None],
) -> int:
    query = select(func.count(AnimeWatch.id)).filter_by(user=user)
    query = query.filter_by(status=status) if status else query
    return await session.scalar(query)


async def get_user_anime_favourite(
    session: AsyncSession,
    user: User,
    limit: int,
    offset: int,
) -> list[AnimeWatch]:
    return await session.scalars(
        select(AnimeFavourite)
        .filter_by(user=user)
        .order_by(desc(AnimeFavourite.created))
        .options(anime_selectinload())
        .limit(limit)
        .offset(offset)
    )


async def get_user_anime_favourite_count(
    session: AsyncSession,
    user: User,
) -> int:
    return await session.scalar(
        select(func.count(AnimeFavourite.id)).filter_by(user=user)
    )
