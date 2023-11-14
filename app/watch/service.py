from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AnimeWatch, Anime, User
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from app.service import anime_loadonly
from .schemas import WatchArgs
from datetime import datetime


async def get_anime_watch(session: AsyncSession, anime: Anime, user: User):
    return await session.scalar(
        select(AnimeWatch).filter(
            AnimeWatch.anime == anime,
            AnimeWatch.user == user,
        )
    )


# ToDo: rewrite this function?
async def save_watch(
    session: AsyncSession, anime: Anime, user: User, args: WatchArgs
):
    # Create watch record if missing
    if not (watch := await get_anime_watch(session, anime, user)):
        watch = AnimeWatch()
        watch.created = datetime.utcnow()
        watch.anime = anime
        watch.user = user

    # Set attributes from args to watch record
    for key, value in args.model_dump().items():
        setattr(watch, key, value)

    # Save watch record
    watch.updated = datetime.utcnow()

    session.add(watch)
    await session.commit()

    return watch


async def delete_watch(session: AsyncSession, watch: AnimeWatch):
    await session.delete(watch)
    await session.commit()


async def get_user_watch_list(
    session: AsyncSession,
    user: User,
    status: str | None,
    limit: int,
    offset: int,
) -> list[AnimeWatch]:
    query = select(AnimeWatch).filter(AnimeWatch.user == user)
    query = query.filter(AnimeWatch.status == status) if status else query

    return await session.scalars(
        query.order_by(desc(AnimeWatch.updated))
        .options(anime_loadonly(selectinload(AnimeWatch.anime)))
        .limit(limit)
        .offset(offset)
    )


async def get_user_watch_list_count(
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
