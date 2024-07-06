from sqlalchemy.ext.asyncio import AsyncSession
from app.models import SystemTimestamp, Log
from datetime import datetime, timedelta
from app.database import sessionmanager
from sqlalchemy import select, asc
from app import constants

from .generate import (
    generate_edit_action,
)


async def generate_moderation(session: AsyncSession):
    edit_delta = timedelta(hours=3)

    # Get system timestamp for latest moderation update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(SystemTimestamp.name == "moderation")
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "moderation",
            }
        )

    # Get new logs that were created since last update
    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_EDIT_ACCEPT,
                    constants.LOG_EDIT_DENY,
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
            constants.LOG_EDIT_ACCEPT,
            constants.LOG_EDIT_DENY,
        ]:
            await generate_edit_action(session, log, edit_delta)

    session.add(system_timestamp)
    await session.commit()


async def update_moderation():
    """Generate moderation history from logs"""

    async with sessionmanager.session() as session:
        await generate_moderation(session)
