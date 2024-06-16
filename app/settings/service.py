from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app import constants
from . import utils

from .schemas import (
    ImportWatchListArgs,
    ImportReadListArgs,
)

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
    Manga,
    Novel,
    User,
    Read,
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


async def delete_user_image(session: AsyncSession, user: User, image_type: str):
    image_id = None

    if image_type == constants.UPLOAD_AVATAR:
        image_id = user.avatar_image_id
        user.avatar_image_id = None

    if image_type == constants.UPLOAD_COVER:
        image_id = user.avatar_image_id = user.cover_image_id
        user.cover_image_id = None

    session.add(user)
    await session.commit()
    await session.refresh(user)

    if image_id:
        await create_log(
            session,
            constants.LOG_SETTINGS_IMAGE_DELETE,
            user,
            data={
                "image_type": image_type,
                "image_id": str(image_id),
            },
        )

    return user


async def delete_user_watch(session: AsyncSession, user: User):
    watch_count = await session.scalar(
        select(func.count(AnimeWatch.id)).filter(
            AnimeWatch.deleted == False,  # noqa: E712
            AnimeWatch.user == user,
        )
    )

    await session.execute(delete(AnimeWatch).filter(AnimeWatch.user == user))
    await session.commit()

    await create_log(
        session,
        constants.LOG_SETTINGS_WATCH_DELETE,
        user,
        data={"watch_count": watch_count},
    )


async def delete_user_read(
    session: AsyncSession, user: User, content_type: str
):
    read_count = await session.scalar(
        select(func.count(Read.id)).filter(
            Read.content_type == content_type,
            Read.deleted == False,  # noqa: E712
            Read.user == user,
        )
    )

    await session.execute(
        delete(Read).filter(
            Read.content_type == content_type,
            Read.user == user,
        )
    )

    await session.commit()

    await create_log(
        session,
        constants.LOG_SETTINGS_READ_DELETE,
        user,
        data={
            "content_type": content_type,
            "read_count": read_count,
        },
    )


async def import_watch_list(
    session: AsyncSession,
    args: ImportWatchListArgs,
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
            select(Anime).filter(
                Anime.mal_id.in_(mal_ids),
                Anime.deleted == False,  # noqa: E712
            )
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
                data.my_comments[:2048]  # NOTE max lenght is 2048 characters
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
                # If anime already in list and user don't want to overwrite it
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
            constants.LOG_SETTINGS_IMPORT_WATCH,
            user,
            data={"imported": imported, "overwrite": args.overwrite},
        )


async def get_read(session: AsyncSession, content: Manga | Novel, user: User):
    return await session.scalar(
        select(Read).filter(
            Read.content_type == content.data_type,
            Read.content_id == content.id,
            Read.deleted == False,  # noqa: E712
            Read.user == user,
        )
    )


async def import_read_list(
    session: AsyncSession,
    args: ImportReadListArgs,
    user: User,
):
    """Import read list"""

    now = utcnow()
    imported_manga = 0
    imported_novel = 0

    # We split list into 20k chunks here due to SQLAlchemy internal limits
    for read_chunk in chunkify(args.content, 20000):
        # Get list of mal_ids for optimized db query
        mal_ids = [entry.manga_mangadb_id for entry in read_chunk]

        # Query list of manga based on mal_ids
        cache = await session.scalars(
            select(Manga).filter(
                Manga.mal_id.in_(mal_ids),
                Manga.deleted == False,  # noqa: E712
            )
        )

        # And build key/value dict
        manga_cache = {entry.mal_id: entry for entry in cache}

        # Now query list of novel based on mal_ids
        cache = await session.scalars(
            select(Novel).filter(
                Novel.mal_id.in_(mal_ids),
                Novel.deleted == False,  # noqa: E712
            )
        )

        # And build key/value dict
        novel_cache = {entry.mal_id: entry for entry in cache}

        content_cache = manga_cache | novel_cache

        for data in read_chunk:
            # If user passed mal_id we don't know about just skip it
            if data.manga_mangadb_id not in content_cache:
                continue

            content = content_cache[data.manga_mangadb_id]

            import_status = utils.get_read_import_status(data.my_status)
            import_note = (
                data.my_comments[:2048]  # NOTE max lenght is 2048 characters
                if isinstance(data.my_comments, str)
                else None
            )

            # Make sure volumes and chaptes count is within our internal limit
            import_chapters = data.my_read_chapters
            import_volumes = data.my_read_volumes

            if import_chapters > 10000:
                import_chapters = 10000

            if import_volumes > 10000:
                import_volumes = 10000

            import_rereads = data.my_times_read

            if import_rereads > 100:
                import_rereads = 100

            if read := await get_read(session, content, user):
                # If content already in list and user don't want to overwrite it
                # Just skipt it
                if not args.overwrite:
                    continue

            else:
                read = Read()
                read.created = now
                read.content_type = content.data_type
                read.content_id = content.id
                read.user = user

            read.chapters = import_chapters
            read.volumes = import_volumes
            read.rereads = import_rereads
            read.status = import_status
            read.score = data.my_score
            read.note = import_note

            read.updated = now

            if read.content_type == constants.CONTENT_MANGA:
                imported_manga += 1

            if read.content_type == constants.CONTENT_NOVEL:
                imported_novel += 1

            session.add(read)

        await session.commit()

    if imported_manga > 0 or imported_novel > 0:
        await create_log(
            session,
            constants.LOG_SETTINGS_IMPORT_READ,
            user,
            data={
                "imported_manga": imported_manga,
                "imported_novel": imported_novel,
                "overwrite": args.overwrite,
            },
        )
