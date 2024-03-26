from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from sqlalchemy import select, asc
from app import constants
import copy

from app.models import (
    SystemTimestamp,
    Collection,
    Log,
)


async def rcalculate_ranking(session: AsyncSession):
    # Get system timestamp for latest ranking update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(SystemTimestamp.name == "ranking")
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "ranking",
            }
        )

    # Get new logs that were created since last update
    logs = await session.scalars(
        select(Log)
        .filter(
            Log.log_type.in_(
                [
                    constants.LOG_FAVOURITE,
                    constants.LOG_FAVOURITE_REMOVE,
                    constants.LOG_COMMENT_WRITE,
                    constants.LOG_COMMENT_HIDE,
                    constants.LOG_VOTE_SET,
                ]
            )
        )
        .filter(Log.created > system_timestamp.timestamp)
        .order_by(asc(Log.created))
    )

    # for log in logs:
    #     # We set timestamp here because after thay it won't be set due to continue
    #     system_timestamp.timestamp = log.created

    #     timestamp = round_day(log.created)

    #     if not (
    #         activity := await session.scalar(
    #             select(Activity).filter(
    #                 Activity.interval == constants.INTERVAL_DAY,
    #                 Activity.timestamp == timestamp,
    #                 Activity.user == log.user,
    #             )
    #         )
    #     ):
    #         activity = Activity(
    #             **{
    #                 "interval": constants.INTERVAL_DAY,
    #                 "timestamp": timestamp,
    #                 "user": log.user,
    #                 "used_logs": [],
    #                 "actions": 0,
    #             }
    #         )

    #     if str(log.id) in activity.used_logs:
    #         continue

    #     # Just leave it here, trust me (SQLAlchemy shenanigans)
    #     activity.used_logs = copy.deepcopy(activity.used_logs)

    #     activity.used_logs.append(str(log.id))
    #     activity.actions = len(activity.used_logs)

    #     session.add(activity)
    #     await session.commit()

    session.add(system_timestamp)
    await session.commit()


async def update_ranking():
    """Recalculare user generateg content ranking from logs"""

    async with sessionmanager.session() as session:
        await rcalculate_ranking(session)
