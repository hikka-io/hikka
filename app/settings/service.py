from sqlalchemy.orm.attributes import set_committed_value
from app.common.schemas import UserCustomizationArgs
from app.watch.service import generate_watch_stats
from sqlalchemy.dialects.postgresql import insert
from app.read.service import generate_read_stats
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.service import create_log
from datetime import datetime
from app import constants
from uuid import UUID
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

from app.models import (
    UserExport,
    AnimeWatch,
    MangaRead,
    NovelRead,
    Anime,
    Manga,
    Novel,
    User,
    Read,
)


async def change_links(session: AsyncSession, user: User, links: list) -> User:
    log_before = user.links

    # I hate this so much but json serializer can't dump it on it's own
    user.links = [link.model_dump(mode="json") for link in links]

    log_after = user.links

    await session.commit()

    if log_before != log_after:
        await create_log(
            session,
            constants.LOG_SETTINGS_LINKS,
            user,
            data={"before": log_before, "after": log_after},
        )

    return user


async def change_description(
    session: AsyncSession, user: User, description: str
) -> User:
    """Change description"""

    log_before = user.description
    user.description = description if description else None
    log_after = user.description

    await session.commit()

    if log_before != log_after:
        await create_log(
            session,
            constants.LOG_SETTINGS_DESCRIPTION,
            user,
            data={"before": log_before, "after": log_after},
        )

    return user


async def set_customization(
    session: AsyncSession, user: User, args: UserCustomizationArgs
) -> User:
    """Change customization"""

    data = args.model_dump()
    log_before = {"preferences": user.preferences, "styles": user.styles}

    user.preferences = data["preferences"]
    user.styles = data["styles"]

    log_after = {"preferences": user.preferences, "styles": user.styles}
    await session.commit()

    if log_before != log_after:
        await create_log(
            session,
            constants.LOG_SETTINGS_CUSTOMIZATION,
            user,
            data={"before": log_before, "after": log_after},
        )

    return user


async def set_username(session: AsyncSession, user: User, username: str):
    """Change username"""

    log_before = user.username
    user.last_username_change = utcnow()
    user.needs_search_update = True
    user.username = username
    log_after = user.username

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
    user.new_email = email
    log_after = user.new_email

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
        image_id = user.cover_image_id
        user.cover_image_id = None

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
            # AnimeWatch.deleted == False,  # noqa: E712
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

    await generate_watch_stats(session, user)


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

    await generate_read_stats(session, user, content_type)


async def get_or_create_watch_entries(
    session: AsyncSession,
    user: User,
    entries: dict[UUID, tuple[Anime, str]],
    now: datetime,
) -> tuple[dict[UUID, AnimeWatch], set[UUID]]:
    """Return user's watch entries for anime and ids of created ones"""

    def select_entries(anime_ids):
        return select(AnimeWatch).filter(
            AnimeWatch.anime_id.in_(anime_ids),
            AnimeWatch.user == user,
        )

    existing = await session.scalars(select_entries(list(entries)))
    watch_cache = {watch.anime_id: watch for watch in existing}

    missing = [anime_id for anime_id in entries if anime_id not in watch_cache]
    created_ids = set()

    if not missing:
        return watch_cache, created_ids

    # Parallel requests may insert same entries
    # so unique index decides which one creates them
    created = await session.scalars(
        insert(AnimeWatch)
        .on_conflict_do_nothing(index_elements=["anime_id", "user_id"])
        .returning(AnimeWatch),
        [
            {
                "status": entries[anime_id][1],
                "anime_id": anime_id,
                "user_id": user.id,
                "created": now,
                "updated": now,
            }
            for anime_id in missing
        ],
    )

    # Here we use set_committed_value to set fields for
    # batch objects from query above
    for watch in created.all():
        set_committed_value(watch, "anime", entries[watch.anime_id][0])
        set_committed_value(watch, "user", user)
        watch_cache[watch.anime_id] = watch
        created_ids.add(watch.anime_id)

    # Entries parallel request created in the meantime
    if skipped := [i for i in missing if i not in created_ids]:
        existing = await session.scalars(select_entries(skipped))
        watch_cache.update({watch.anime_id: watch for watch in existing})

    return watch_cache, created_ids


async def get_or_create_read_entries(
    session: AsyncSession,
    user: User,
    entries: dict[UUID, tuple[Manga | Novel, str]],
    now: datetime,
) -> tuple[dict[UUID, Read], set[UUID]]:
    """Return user's read entries for content and ids of created ones"""

    def select_entries(content_ids):
        return select(Read).filter(
            Read.deleted == False,  # noqa: E712
            Read.content_id.in_(content_ids),
            Read.user == user,
        )

    existing = await session.scalars(select_entries(list(entries)))
    read_cache = {read.content_id: read for read in existing}

    missing = [
        content_id for content_id in entries if content_id not in read_cache
    ]

    created_ids = set()

    # Read entries are inserted with their own model to get it back
    for read_model, content_type in [
        (MangaRead, constants.CONTENT_MANGA),
        (NovelRead, constants.CONTENT_NOVEL),
    ]:
        values = [
            {
                "status": entries[content_id][1],
                "content_type": content_type,
                "content_id": content_id,
                "user_id": user.id,
                "created": now,
                "updated": now,
            }
            for content_id in missing
            if entries[content_id][0].data_type == content_type
        ]

        if not values:
            continue

        # Parallel requests may insert same entries
        # so unique index decides which one creates them
        created = await session.scalars(
            insert(read_model)
            .on_conflict_do_nothing(
                index_elements=["content_type", "content_id", "user_id"],
                index_where=Read.deleted == False,  # noqa: E712
            )
            .returning(read_model),
            values,
        )

        # Here we use set_committed_value to set fields for
        # batch objects from query above
        for read in created.all():
            set_committed_value(read, "content", entries[read.content_id][0])
            set_committed_value(read, "user", user)
            read_cache[read.content_id] = read
            created_ids.add(read.content_id)

    # Entries parallel request created in the meantime
    if skipped := [i for i in missing if i not in created_ids]:
        existing = await session.scalars(select_entries(skipped))
        read_cache.update({read.content_id: read for read in existing})

    return read_cache, created_ids


async def import_watch_list(
    session: AsyncSession,
    args: ImportWatchListArgs,
    user: User,
):
    """Import watch list"""

    now = utcnow()
    imported = 0

    # We split list into 20k chunks here due to SQLAlchemy internal limits
    for anime_chunk in chunkify(args.anime, constants.ALCHEMY_CHUNK_LIMIT):
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

        # New entries get status from first time anime appears in list
        entries = {}

        for data in anime_chunk:
            anime = anime_cache.get(data.series_animedb_id)

            if anime and anime.id not in entries:
                entries[anime.id] = (
                    anime,
                    utils.get_anime_import_status(data.my_status),
                )

        watch_cache, created_ids = await get_or_create_watch_entries(
            session, user, entries, now
        )

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

            if not (watch := watch_cache.get(anime.id)):
                continue

            # Repeated anime in the same list counts as existing entry
            created = anime.id in created_ids
            created_ids.discard(anime.id)

            # If anime already in list and user don't want to overwrite it
            # Just skipt it
            if not created and not args.overwrite:
                continue

            watch.rewatches = import_rewatches
            watch.episodes = import_episodes
            watch.status = import_status
            watch.score = data.my_score
            watch.note = import_note

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

        await generate_watch_stats(session, user)


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
    for read_chunk in chunkify(args.content, constants.ALCHEMY_CHUNK_LIMIT):
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

        # New entries get status from first time content appears in list
        entries = {}

        for data in read_chunk:
            content = content_cache.get(data.manga_mangadb_id)

            if content and content.id not in entries:
                entries[content.id] = (
                    content,
                    utils.get_read_import_status(data.my_status),
                )

        read_cache, created_ids = await get_or_create_read_entries(
            session, user, entries, now
        )

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

            if not (read := read_cache.get(content.id)):
                continue

            # Repeated content in the same list counts as existing entry
            created = content.id in created_ids
            created_ids.discard(content.id)

            # If content already in list and user don't want to overwrite it
            # Just skipt it
            if not created and not args.overwrite:
                continue

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

        if imported_manga > 0:
            await generate_read_stats(session, user, constants.CONTENT_MANGA)

        if imported_novel > 0:
            await generate_read_stats(session, user, constants.CONTENT_NOVEL)


async def get_export_list(session: AsyncSession, user: User):
    if not (
        export := await session.scalar(
            select(UserExport).filter(UserExport.user == user)
        )
    ):
        now = utcnow()

        export = UserExport(
            **{
                "created": now,
                "updated": now,
                "user": user,
            }
        )

        session.add(export)
        await session.commit()

    return export
