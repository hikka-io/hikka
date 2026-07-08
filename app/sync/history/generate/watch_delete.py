from sqlalchemy.ext.asyncio import AsyncSession
from app.models import History, Review, Log
from datetime import timedelta
from sqlalchemy import select
from app import constants
from .. import service


async def generate_watch_delete(
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

    if history:
        await session.delete(history)

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

    # Set score to zero if list entry is deleted
    if review := await session.scalar(
        select(Review).filter(
            Review.content_type == constants.CONTENT_ANIME,
            Review.content_id == log.target_id,
            Review.author_id == log.user_id,
        )
    ):
        review.score = 0

    await session.commit()
