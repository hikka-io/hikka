from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import ImportAnimeListArgs
from app.service import get_anime_watch
from app.utils import hashpwd, chunkify
from sqlalchemy import select
from datetime import datetime
from . import utils

from app.models import (
    AnimeWatch,
    Anime,
    User,
)


async def change_description(
    session: AsyncSession, user: User, description: str
) -> User:
    """Change description"""

    user.description = description if description else None

    session.add(user)
    await session.commit()

    return user


async def set_username(session: AsyncSession, user: User, username: str):
    """Changed username"""

    user.last_username_change = datetime.utcnow()
    user.username = username

    session.add(user)
    await session.commit()

    return user


async def set_email(session: AsyncSession, user: User, email: str):
    """Changed email"""

    user.last_email_change = datetime.utcnow()
    user.email_confirmed = False
    user.email = email

    session.add(user)
    await session.commit()

    return user


async def set_password(session: AsyncSession, user: User, password: str):
    """Changed password"""

    user.password_hash = hashpwd(password)

    session.add(user)
    await session.commit()

    return user


async def import_watch_list(
    session: AsyncSession,
    args: ImportAnimeListArgs,
    user: User,
):
    """Import watch list"""

    now = datetime.utcnow()

    # We split list into 20k chunks here due to SQLAlchemy internal limits
    for anime_chunk in chunkify(args.anime, 20000):
        # Get list of mal_ids for optimized db query
        mal_ids = [entry.series_animedb_id for entry in anime_chunk]

        # Query list of anime based on mal_ids
        cache = await session.scalars(
            select(Anime).where(Anime.mal_id.in_(mal_ids))
        )

        # And build key/value dict
        anime_cache = {entry.mal_id: entry for entry in cache}

        for data in anime_chunk:
            # If user passed mal_id we don't know about just skip it
            if data.series_animedb_id not in anime_cache:
                continue

            anime = anime_cache[data.series_animedb_id]

            import_status = utils.get_anime_import_status(data.my_status)
            import_note = (
                data.my_comments[:140]  # Note max lenght is 140 characters
                if isinstance(data.my_comments, str)
                else None
            )

            # Make sure episodes count is within our internal limit
            import_episodes = data.my_watched_episodes

            if import_episodes > 10000:
                import_episodes = 10000

            if anime.episodes_total and import_episodes > anime.episodes_total:
                import_episodes = anime.episodes_total

            if watch := await get_anime_watch(session, anime, user):
                # If anime already in list and usrer don't want to overwrite it
                # Just skipt it
                if not args.overwrite:
                    continue

            else:
                watch = AnimeWatch()
                watch.created = now
                watch.anime = anime
                watch.user = user

            watch.episodes = import_episodes
            watch.status = import_status
            watch.score = data.my_score
            watch.note = import_note
            watch.updated = now

            session.add(watch)

        await session.commit()
