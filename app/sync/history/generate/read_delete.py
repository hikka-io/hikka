from sqlalchemy.ext.asyncio import AsyncSession
from app.models import History, Log
from datetime import timedelta
from app import constants
from .. import service


async def generate_read_delete(
    session: AsyncSession,
    log: Log,
    read_delta: timedelta,
):
    threshold = log.created - read_delta

    history_type = (
        constants.HISTORY_READ_MANGA
        if log.data["content_type"] == constants.CONTENT_MANGA
        else constants.HISTORY_READ_NOVEL
    )

    history_type_delte = (
        constants.HISTORY_READ_MANGA_DELETE
        if log.data["content_type"] == constants.CONTENT_MANGA
        else constants.HISTORY_READ_NOVEL_DELETE
    )

    history = await service.get_history(
        session,
        history_type,
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
                "history_type": history_type_delte,
                "used_logs": [str(log.id)],
                "target_id": log.target_id,
                "user_id": log.user_id,
                "created": log.created,
                "updated": log.created,
            }
        )

        session.add(history)
        await session.commit()
