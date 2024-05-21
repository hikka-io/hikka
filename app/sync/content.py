from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmanager
from sqlalchemy import update, delete
from sqlalchemy import select, asc
from datetime import datetime
from app import constants

from app.models import (
    SystemTimestamp,
    AnimeFavourite,
    AnimeSchedule,
    AnimeComment,
    AnimeWatch,
    AnimeEdit,
    Anime,
    Log,
)


async def process_content_deleted(session: AsyncSession):
    # Get system timestamp for latest content_deleted update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(
                SystemTimestamp.name == "content_deleted"
            )
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "content_deleted",
            }
        )

    # Get new logs that were created since last update
    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_CONTENT_DELETED,
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    for log in logs:
        # We set timestamp here because after thay it won't be set due to continue
        system_timestamp.timestamp = log.created

        if log.log_type == constants.LOG_CONTENT_DELETED:
            # We can recover schedule from aggregator if needed
            await session.execute(
                delete(AnimeSchedule).filter(
                    AnimeSchedule.anime_id == log.target_id
                )
            )

            # Here we mark anime related models as deleted
            # instead of actually deleting them so they can be
            # recovered if needed (for example if anime was deleted by accident)
            await session.execute(
                update(AnimeComment)
                .filter(AnimeComment.content_id == log.target_id)
                .values(deleted=True)
            )

            await session.execute(
                update(AnimeFavourite)
                .filter(AnimeFavourite.content_id == log.target_id)
                .values(deleted=True)
            )

            await session.execute(
                update(AnimeWatch)
                .filter(AnimeWatch.anime_id == log.target_id)
                .values(deleted=True)
            )

            await session.execute(
                update(AnimeEdit)
                .filter(AnimeEdit.content_id == log.target_id)
                .values(hidden=True)
            )

            anime = await session.scalar(
                select(Anime).filter(Anime.id == log.target_id)
            )

            print(f"Deleted anime {anime.title_ja}")

    session.add(system_timestamp)
    await session.commit()


async def update_content():
    """Update content"""

    async with sessionmanager.session() as session:
        await process_content_deleted(session)
