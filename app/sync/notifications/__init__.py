from sqlalchemy.ext.asyncio import AsyncSession
from app.models import SystemTimestamp, Log
from app.database import sessionmanager
from sqlalchemy import select, asc
from datetime import datetime
from app import constants

from .generate import (
    generate_thirdparty_login,
    generate_collection_vote,
    generate_anime_schedule,
    generate_comment_write,
    generate_comment_vote,
    generate_edit_update,
    generate_edit_accept,
    generate_edit_deny,
    generate_follow,
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
                    constants.LOG_LOGIN_THIRDPARTY,
                    constants.LOG_SCHEDULE_ANIME,
                    constants.LOG_COMMENT_WRITE,
                    constants.LOG_EDIT_UPDATE,
                    constants.LOG_EDIT_ACCEPT,
                    constants.LOG_EDIT_DENY,
                    constants.LOG_VOTE_SET,
                    constants.LOG_FOLLOW,
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    for log in logs:
        # We set timestamp here because after thay it won't be set due to continue
        system_timestamp.timestamp = log.created

        if log.log_type == constants.LOG_VOTE_SET:
            if log.data["content_type"] == constants.CONTENT_COMMENT:
                await generate_comment_vote(session, log)

            if log.data["content_type"] == constants.CONTENT_COLLECTION:
                await generate_collection_vote(session, log)

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

        # Create batch user notifications after anime aired
        if log.log_type == constants.LOG_SCHEDULE_ANIME:
            await generate_anime_schedule(session, log)

        if log.log_type == constants.LOG_FOLLOW:
            await generate_follow(session, log)

        if log.log_type == constants.LOG_LOGIN_THIRDPARTY:
            await generate_thirdparty_login(session, log)

    session.add(system_timestamp)
    await session.commit()


async def update_notifications():
    """Generate users notifications from logs"""

    async with sessionmanager.session() as session:
        await generate_notifications(session)
