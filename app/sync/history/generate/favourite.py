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

    history_type = {
        constants.CONTENT_ANIME: constants.HISTORY_FAVOURITE_ANIME,
        constants.CONTENT_MANGA: constants.HISTORY_FAVOURITE_MANGA,
        constants.CONTENT_NOVEL: constants.HISTORY_FAVOURITE_NOVEL,
    }.get(log.data["content_type"])

    history = await service.get_history(
        session,
        history_type,
        log.target_id,
        log.user_id,
        threshold,
    )

    if not history:
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
