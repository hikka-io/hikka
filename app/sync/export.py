from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import to_timestamp, utcnow
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from sqlalchemy import select, asc
from datetime import datetime
from app import constants
from uuid import UUID

from app.models import (
    SystemTimestamp,
    UserExport,
    AnimeWatch,
    MangaRead,
    NovelRead,
    Anime,
    Manga,
    Novel,
    User,
    Log,
)


async def get_export_data(session: AsyncSession, user_id: UUID):
    watch_list = await session.scalars(
        select(AnimeWatch)
        .filter(AnimeWatch.user_id == user_id)
        .options(
            selectinload(AnimeWatch.anime).load_only(Anime.mal_id, Anime.slug)
        )
        .order_by(AnimeWatch.updated.desc(), AnimeWatch.created.desc())
    )

    manga_read_list = await session.scalars(
        select(MangaRead)
        .filter(MangaRead.user_id == user_id)
        .options(
            selectinload(MangaRead.content).load_only(Manga.mal_id, Manga.slug)
        )
        .order_by(MangaRead.updated.desc(), MangaRead.created.desc())
    )

    novel_read_list = await session.scalars(
        select(NovelRead)
        .filter(NovelRead.user_id == user_id)
        .options(
            selectinload(NovelRead.content).load_only(Novel.mal_id, Novel.slug)
        )
        .order_by(NovelRead.updated.desc(), NovelRead.created.desc())
    )

    return {
        "anime": [
            {
                "mal_id": watch.anime.mal_id,
                "hikka_slug": watch.anime.slug,
                "created": to_timestamp(watch.created),
                "updated": to_timestamp(watch.updated),
                "rewatches": watch.rewatches,
                "episodes": watch.episodes,
                "status": watch.status,
                "score": watch.score,
                "note": watch.note,
            }
            for watch in watch_list
        ],
        "manga": [
            {
                "mal_id": read.content.mal_id,
                "hikka_slug": read.content.slug,
                "created": to_timestamp(read.created),
                "updated": to_timestamp(read.updated),
                "chapters": read.chapters,
                "volumes": read.volumes,
                "rereads": read.rereads,
                "status": read.status,
                "score": read.score,
                "note": read.note,
            }
            for read in manga_read_list
        ],
        "novel": [
            {
                "mal_id": read.content.mal_id,
                "hikka_slug": read.content.slug,
                "created": to_timestamp(read.created),
                "updated": to_timestamp(read.updated),
                "chapters": read.chapters,
                "volumes": read.volumes,
                "rereads": read.rereads,
                "status": read.status,
                "score": read.score,
                "note": read.note,
            }
            for read in novel_read_list
        ],
    }


async def generate_export(session: AsyncSession):
    # Get system timestamp for latest export update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(SystemTimestamp.name == "export")
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2025, 2, 25),
                "name": "export",
            }
        )

    # Get new logs that were created since last update
    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_WATCH_CREATE,
                    constants.LOG_WATCH_UPDATE,
                    constants.LOG_WATCH_DELETE,
                    constants.LOG_READ_CREATE,
                    constants.LOG_READ_UPDATE,
                    constants.LOG_READ_DELETE,
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    user_ids = []

    for log in logs:
        # We set timestamp here because after thay it won't be set due to continue
        system_timestamp.timestamp = log.created

        # Here we add user ids to list which will be porcessed further on
        if log.user_id not in user_ids:
            user_ids.append(log.user_id)

    # Getting users which interacted with their list
    users = await session.scalars(
        select(User).filter(User.id.in_(list(set(user_ids))))
    )

    now = utcnow()

    # And generating export record for them
    for user in users:
        exported_list = await get_export_data(session, user.id)

        if not (
            export := await session.scalar(
                select(UserExport).filter(UserExport.user == user)
            )
        ):
            export = UserExport(
                **{
                    "created": now,
                    "updated": now,
                    "user": user,
                }
            )

        export.anime = exported_list["anime"]
        export.manga = exported_list["manga"]
        export.novel = exported_list["novel"]
        export.updated = now

        session.add(export)

        print(f"Generated export for {user.username}")

    session.add(system_timestamp)
    await session.commit()


async def update_export():
    """Generate users export from logs"""

    async with sessionmanager.session() as session:
        await generate_export(session)
