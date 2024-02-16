from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from sqlalchemy import select, asc
from app import constants
import copy

from app.models import (
    SystemTimestamp,
    Activity,
    Log,
)


def round_day(date):
    return date - timedelta(
        days=date.day % 1,
        hours=date.hour,
        minutes=date.minute,
        seconds=date.second,
        microseconds=date.microsecond,
    )


async def generate_activity(session: AsyncSession):
    # Get system timestamp for latest activity update
    if not (
        system_timestamp := await session.scalar(
            select(SystemTimestamp).filter(SystemTimestamp.name == "activity")
        )
    ):
        system_timestamp = SystemTimestamp(
            **{
                "timestamp": datetime(2024, 1, 13),
                "name": "activity",
            }
        )

    # Get new logs that were created since last update
    logs = await session.scalars(
        select(Log)
        .filter(Log.created > system_timestamp.timestamp)
        .options(selectinload(Log.user))
        .order_by(asc(Log.created))
    )

    for log in logs:
        # We set timestamp here because after thay it won't be set due to continue
        system_timestamp.timestamp = log.created

        timestamp = round_day(log.created)

        if not (
            activity := await session.scalar(
                select(Activity).filter(
                    Activity.interval == constants.INTERVAL_DAY,
                    Activity.timestamp == timestamp,
                    Activity.user == log.user,
                )
            )
        ):
            activity = Activity(
                **{
                    "interval": constants.INTERVAL_DAY,
                    "timestamp": timestamp,
                    "user": log.user,
                    "used_logs": [],
                    "actions": 0,
                }
            )

        if str(log.id) in activity.used_logs:
            continue

        # Just leave it here, trust me (SQLAlchemy shenanigans)
        activity.used_logs = copy.deepcopy(activity.used_logs)

        activity.used_logs.append(str(log.id))
        activity.actions = len(activity.used_logs)

        session.add(activity)
        await session.commit()

    session.add(system_timestamp)
    await session.commit()


async def update_activity():
    """Generate users activity from logs"""

    async with sessionmanager.session() as session:
        await generate_activity(session)
