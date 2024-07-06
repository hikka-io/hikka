from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Moderation, Log
from datetime import timedelta
from app import constants
from ...moderation import service


async def generate_edit_action(
    session: AsyncSession,
    log: Log,
    edit_delta: timedelta,
):
    threshold = log.created - edit_delta

    history_type = {
        constants.EDIT_ACCEPTED: constants.HISTORY_EDIT_ACCEPT,
        constants.EDIT_DENIED: constants.HISTORY_EDIT_DENY,
    }.get(log.data["content_type"])

    if not history_type:
        return

    moderation = await service.get_moderation(
        session,
        history_type,
        log.target_id,
        log.user_id,
        threshold,
    )

    if not moderation:
        moderation = Moderation(
            **{
                "history_type": history_type,
                "used_logs": [str(log.id)],
                "target_id": log.target_id,
                "user_id": log.user_id,
                "created": log.created,
            }
        )

        session.add(moderation)
        await session.commit()
