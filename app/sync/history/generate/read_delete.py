from sqlalchemy.ext.asyncio import AsyncSession
from app.models import History, Review, Log
from datetime import timedelta
from sqlalchemy import select
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

    history_type_delete = (
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

    else:
        history = History(
            **{
                "history_type": history_type_delete,
                "used_logs": [str(log.id)],
                "target_id": log.target_id,
                "user_id": log.user_id,
                "created": log.created,
                "updated": log.created,
            }
        )

        session.add(history)

    # Update review score if it exists
    if review := await session.scalar(
        select(Review).filter(
            Review.content_type == log.data["content_type"],
            Review.content_id == log.target_id,
            Review.author_id == log.user_id,
        )
    ):
        review.score = 0

    await session.commit()
