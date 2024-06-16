from sqlalchemy.ext.asyncio import AsyncSession
from app.models import SystemTimestamp, Log
from datetime import datetime, timedelta
from app.database import sessionmanager
from sqlalchemy import select, asc
from app import constants

from .generate import (
    generate_favourite_delete,
    generate_watch_delete,
    generate_read_delete,
    generate_favourite,
    generate_import,
    generate_watch,
    generate_read,
)


async def generate_history(session: AsyncSession):
    favourite_delta = timedelta(hours=6)
    watch_delta = timedelta(hours=3)
    read_delta = timedelta(hours=3)

    # Get system timestamp for latest history update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(SystemTimestamp.name == "history")
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "history",
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
                    constants.LOG_FAVOURITE,
                    constants.LOG_FAVOURITE_REMOVE,
                    constants.LOG_SETTINGS_IMPORT_WATCH,
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    for log in logs:
        # We set timestamp here because after thay it won't be set due to continue
        system_timestamp.timestamp = log.created

        if log.log_type in [
            constants.LOG_WATCH_UPDATE,
            constants.LOG_WATCH_CREATE,
        ]:
            await generate_watch(session, log, watch_delta)

        if log.log_type in [
            constants.LOG_READ_UPDATE,
            constants.LOG_READ_CREATE,
        ]:
            await generate_read(session, log, read_delta)

        if log.log_type == constants.LOG_WATCH_DELETE:
            await generate_watch_delete(session, log, watch_delta)

        if log.log_type == constants.LOG_READ_DELETE:
            await generate_read_delete(session, log, read_delta)

        if log.log_type == constants.LOG_FAVOURITE:
            await generate_favourite(session, log, favourite_delta)

        if log.log_type == constants.LOG_FAVOURITE_REMOVE:
            await generate_favourite_delete(session, log, favourite_delta)

        if log.log_type == constants.LOG_SETTINGS_IMPORT_WATCH:
            await generate_import(session, log)

    session.add(system_timestamp)
    await session.commit()


async def update_history():
    """Generate users history from logs"""

    async with sessionmanager.session() as session:
        await generate_history(session)
