from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import ImportAnimeListArgs
from sqlalchemy import select
from app import constants
from . import utils

from app.utils import (
    chunkify,
    hashpwd,
    utcnow,
)

from app.service import (
    calculate_watch_duration,
    get_anime_watch,
    create_log,
)

from app.models import (
    AnimeWatch,
    Anime,
    User,
)


async def change_description(
    session: AsyncSession, user: User, description: str
) -> User:
    """Change description"""

    log_before = user.description
    user.description = description if description else None
    log_after = user.description

    session.add(user)
    await session.commit()

    if log_before != log_after:
        await create_log(
            session,
            constants.LOG_SETTINGS_DESCRIPTION,
            user,
            data={"before": log_before, "after": log_after},
        )

    return user


async def set_username(session: AsyncSession, user: User, username: str):
    """Changed username"""

    log_before = user.username
    user.last_username_change = utcnow()
    user.needs_search_update = True
    user.username = username
    log_after = user.username

    session.add(user)
    await session.commit()

    if log_before != log_after:
        await create_log(
            session,
            constants.LOG_SETTINGS_USERNAME,
            user,
            data={"before": log_before, "after": log_after},
        )

    return user


async def set_email(session: AsyncSession, user: User, email: str):
    """Changed email"""

    log_before = user.email
    user.last_email_change = utcnow()
    user.email_confirmed = False
    user.email = email
    log_after = user.email

    session.add(user)
    await session.commit()

    if log_before != log_after:
        await create_log(
            session,
            constants.LOG_SETTINGS_EMAIL,
            user,
            data={"before": log_before, "after": log_after},
        )

    return user


async def set_password(session: AsyncSession, user: User, password: str):
    """Changed password"""

    user.password_hash = hashpwd(password)

    session.add(user)
    await session.commit()

    await create_log(session, constants.LOG_SETTINGS_PASSWORD, user)

    return user


async def import_watch_list(
    session: AsyncSession,
    args: ImportAnimeListArgs,
    user: User,
):
    """Import watch list"""

    now = utcnow()
    imported = 0

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
                data.my_comments[:2048]  # Note max lenght is 2048 characters
                if isinstance(data.my_comments, str)
                else None
            )

            # Make sure episodes count is within our internal limit
            import_episodes = data.my_watched_episodes

            if import_episodes > 10000:
                import_episodes = 10000

            import_rewatches = data.my_times_watched

            if import_rewatches > 100:
                import_rewatches = 100

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

            watch.rewatches = import_rewatches
            watch.episodes = import_episodes
            watch.status = import_status
            watch.score = data.my_score
            watch.note = import_note

            watch.duration = calculate_watch_duration(watch)
            watch.updated = now

            imported += 1

            session.add(watch)

        await session.commit()

    if imported > 0:
        await create_log(
            session,
            constants.LOG_SETTINGS_IMPORT,
            user,
            data={"imported": imported, "overwrite": args.overwrite},
        )


async def set_ignored_notifications(
    session: AsyncSession, user: User, ignored_notifications: list[str]
):
    """Changed ignored notifications"""

    log_before = user.ignored_notifications
    user.ignored_notifications = ignored_notifications
    log_after = user.ignored_notifications

    session.add(user)
    await session.commit()

    if log_before != log_after:
        await create_log(
            session,
            constants.LOG_SETTINGS_IGNORED_NOTIFICATIONS,
            user,
            data={"before": log_before, "after": log_after},
        )

    return user
