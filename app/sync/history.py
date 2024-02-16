from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from datetime import datetime, timedelta
from app.database import sessionmanager
from app import constants
from uuid import UUID
import copy

from app.models import (
    SystemTimestamp,
    History,
    Log,
)


async def get_history(
    session: AsyncSession,
    history_type: str,
    target_id: UUID,
    user_id: UUID,
    threshold: datetime,
):
    return await session.scalar(
        select(History)
        .filter(
            History.history_type == history_type,
            History.target_id == target_id,
            History.user_id == user_id,
            History.created > threshold,
        )
        .order_by(desc(History.updated), desc(History.created))
    )


async def generate_history(session: AsyncSession):
    favourite_delta = timedelta(hours=6)
    watch_delta = timedelta(hours=3)

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
                    constants.LOG_FAVOURITE_ANIME,
                    constants.LOG_FAVOURITE_ANIME_REMOVE,
                    constants.LOG_SETTINGS_IMPORT,
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
            threshold = log.created - watch_delta

            history = await get_history(
                session,
                constants.HISTORY_WATCH,
                log.target_id,
                log.user_id,
                threshold,
            )

            if not history:
                new_watch = log.log_type == constants.LOG_WATCH_CREATE
                history = History(
                    **{
                        "history_type": constants.HISTORY_WATCH,
                        "target_id": log.target_id,
                        "user_id": log.user_id,
                        "created": log.created,
                        "used_logs": [],
                        "data": {
                            "new_watch": new_watch,
                            "before": {},
                            "after": {},
                        },
                    }
                )

            if str(log.id) in history.used_logs:
                continue

            # Just leave it here, trust me (SQLAlchemy shenanigans)
            history.data = copy.deepcopy(history.data)
            history.used_logs = copy.deepcopy(history.used_logs)

            # Only record unknown keys to before
            for key in log.data["before"]:
                if key not in history.data["before"]:
                    history.data["before"][key] = log.data["before"][key]

            # Update all keys in after
            for key in log.data["after"]:
                history.data["after"][key] = log.data["after"][key]

            history.used_logs.append(str(log.id))
            history.updated = log.created

            session.add(history)
            await session.commit()

        if log.log_type == constants.LOG_WATCH_DELETE:
            threshold = log.created - watch_delta

            history = await get_history(
                session,
                constants.HISTORY_WATCH,
                log.target_id,
                log.user_id,
                threshold,
            )

            if history:
                await session.delete(history)
                await session.commit()

            else:
                history = History(
                    **{
                        "history_type": constants.HISTORY_WATCH_DELETE,
                        "used_logs": [str(log.id)],
                        "target_id": log.target_id,
                        "user_id": log.user_id,
                        "created": log.created,
                        "updated": log.created,
                    }
                )

                session.add(history)
                await session.commit()

        if log.log_type == constants.LOG_FAVOURITE_ANIME:
            threshold = log.created - favourite_delta

            history = await get_history(
                session,
                constants.HISTORY_FAVOURITE_ANIME,
                log.target_id,
                log.user_id,
                threshold,
            )

            if not history:
                history = History(
                    **{
                        "history_type": constants.HISTORY_FAVOURITE_ANIME,
                        "used_logs": [str(log.id)],
                        "target_id": log.target_id,
                        "user_id": log.user_id,
                        "created": log.created,
                        "updated": log.created,
                    }
                )

                session.add(history)
                await session.commit()

        if log.log_type == constants.LOG_FAVOURITE_ANIME_REMOVE:
            threshold = log.created - favourite_delta

            history = await get_history(
                session,
                constants.HISTORY_FAVOURITE_ANIME,
                log.target_id,
                log.user_id,
                threshold,
            )

            if history:
                await session.delete(history)
                await session.commit()

            else:
                # For sake of clean code
                history_type = constants.HISTORY_FAVOURITE_ANIME_REMOVE
                history = History(
                    **{
                        "history_type": history_type,
                        "used_logs": [str(log.id)],
                        "target_id": log.target_id,
                        "user_id": log.user_id,
                        "created": log.created,
                        "updated": log.created,
                    }
                )

                session.add(history)
                await session.commit()

        if log.log_type == constants.LOG_SETTINGS_IMPORT:
            history = History(
                **{
                    "history_type": constants.HISTORY_WATCH_IMPORT,
                    "used_logs": [str(log.id)],
                    "user_id": log.user_id,
                    "created": log.created,
                    "updated": log.created,
                    "target_id": None,
                    "data": log.data,
                }
            )

            session.add(history)
            await session.commit()

    session.add(system_timestamp)
    await session.commit()


async def update_history():
    """Generate users history from logs"""

    async with sessionmanager.session() as session:
        await generate_history(session)
