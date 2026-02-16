from sqlalchemy.ext.asyncio import AsyncSession
from app.models import SystemTimestamp, Log
from app.database import sessionmanager
from sqlalchemy import select, asc
from datetime import datetime
from app import constants

from .generate import (
    generate_collection_delete,
    generate_collection_update,
    generate_comment_hide,
    generate_edit_accept,
    generate_edit_update,
    generate_edit_deny,
)


async def generate_moderation(session: AsyncSession):
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

    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_EDIT_ACCEPT,
                    constants.LOG_EDIT_DENY,
                    constants.LOG_EDIT_UPDATE,
                    constants.LOG_COMMENT_HIDE,
                    constants.LOG_COLLECTION_DELETE,
                    constants.LOG_COLLECTION_UPDATE,
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    for log in logs:
        system_timestamp.timestamp = log.created

        match log.log_type:
            case constants.LOG_EDIT_ACCEPT:
                await generate_edit_accept(session, log)

            case constants.LOG_EDIT_DENY:
                await generate_edit_deny(session, log)

            case constants.LOG_EDIT_UPDATE:
                await generate_edit_update(session, log)

            case constants.LOG_COMMENT_HIDE:
                await generate_comment_hide(session, log)

            case constants.LOG_COLLECTION_DELETE:
                await generate_collection_delete(session, log)

            case constants.LOG_COLLECTION_UPDATE:
                await generate_collection_update(session, log)

    session.add(system_timestamp)
    await session.commit()


async def update_moderation():
    """Generate moderation log from logs"""

    async with sessionmanager.session() as session:
        await generate_moderation(session)
