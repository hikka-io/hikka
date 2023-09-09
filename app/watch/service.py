from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AnimeWatch, Anime, User
from .schemas import WatchArgs
from sqlalchemy import select
from datetime import datetime


async def get_anime_watch(session: AsyncSession, anime: Anime, user: User):
    return await session.scalar(
        select(AnimeWatch).filter(
            AnimeWatch.anime == anime, AnimeWatch.user == user
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
    for key, value in args.dict().items():
        setattr(watch, key, value)

    # Save watch record
    watch.updated = datetime.utcnow()

    session.add(watch)
    await session.commit()

    return watch


async def delete_watch(session: AsyncSession, watch: AnimeWatch):
    await session.delete(watch)
    await session.commit()
