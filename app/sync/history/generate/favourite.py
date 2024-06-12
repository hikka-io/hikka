from sqlalchemy.ext.asyncio import AsyncSession
from app.models import History, Log
from datetime import timedelta
from app import constants
from .. import service


async def generate_favourite(
    session: AsyncSession,
    log: Log,
    favourite_delta: timedelta,
):
    threshold = log.created - favourite_delta

    if log.data["content_type"] == constants.CONTENT_ANIME:
        history = await service.get_history(
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
