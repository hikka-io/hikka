from sqlalchemy.ext.asyncio import AsyncSession
from app.models import SystemTimestamp, Log
from app.database import sessionmanager
from sqlalchemy import select, asc
from datetime import datetime
from app import constants

from .generate import (
    generate_comment_write,
    generate_comment_vote,
    generate_edit_update,
    generate_edit_accept,
    generate_edit_deny,
)


async def generate_notifications(session: AsyncSession):
    # Get system timestamp for latest history update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(
                SystemTimestamp.name == "notifications"
            )
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "notifications",
            }
        )

    # Get new logs that were created since last update
    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_COMMENT_WRITE,
                    constants.LOG_COMMENT_VOTE,
                    constants.LOG_EDIT_ACCEPT,
                    constants.LOG_EDIT_DENY,
                    constants.LOG_EDIT_UPDATE,  # ToDo
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    for log in logs:
        # We set timestamp here because after thay it won't be set due to continue
        system_timestamp.timestamp = log.created

        if log.log_type == constants.LOG_COMMENT_VOTE:
            await generate_comment_vote(session, log)

        if log.log_type == constants.LOG_COMMENT_WRITE:
            await generate_comment_write(session, log)

        # Create notification for edit author if edit was accepted
        if log.log_type == constants.LOG_EDIT_ACCEPT:
            await generate_edit_accept(session, log)

        # Create notification for edit author if edit was denied
        if log.log_type == constants.LOG_EDIT_DENY:
            await generate_edit_deny(session, log)

        # Create notification for edit author if edit was denied
        if log.log_type == constants.LOG_EDIT_UPDATE:
            await generate_edit_update(session, log)

    session.add(system_timestamp)
    await session.commit()


async def update_notifications():
    """Generate users notifications from logs"""

    async with sessionmanager.session() as session:
        await generate_notifications(session)
