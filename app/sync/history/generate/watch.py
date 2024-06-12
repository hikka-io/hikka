from sqlalchemy.ext.asyncio import AsyncSession
from app.models import History, Log
from datetime import timedelta
from app import constants
from .. import service
import copy


async def generate_watch(
    session: AsyncSession,
    log: Log,
    watch_delta: timedelta,
):
    threshold = log.created - watch_delta

    history = await service.get_history(
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
        return

    # Just leave it here, trust me (SQLAlchemy shenanigans)
    history.data = copy.deepcopy(history.data)
    history.used_logs = copy.deepcopy(history.used_logs)

    # Only record unknown keys to before
    for key in log.data["before"]:
        # Skip edited notes
        if key == "note":
            continue

        if key not in history.data["before"]:
            history.data["before"][key] = log.data["before"][key]

    # Update all keys in after
    for key in log.data["after"]:
        # Skip edited notes here too
        if key == "note":
            continue

        history.data["after"][key] = log.data["after"][key]

    history.used_logs.append(str(log.id))
    history.updated = log.created

    # Skip empty history edits
    if history.data["before"] == {} and history.data["after"] == {}:
        return

    session.add(history)
    await session.commit()
