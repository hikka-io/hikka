from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, AnimeWatch, Anime
from sqlalchemy.orm import selectinload
from sqlalchemy import select, desc
from sqlalchemy import func


async def get_user_watch(
    session: AsyncSession, user: User, limit: int, offset: int
):
    return await session.scalars(
        select(AnimeWatch)
        .filter_by(user=user)
        .order_by(desc(AnimeWatch.updated))
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


async def get_user_watch_count(session: AsyncSession, user: User):
    return await session.scalar(
        select(func.count(AnimeWatch.id)).filter_by(user=user)
    )
