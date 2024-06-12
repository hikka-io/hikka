from sqlalchemy.ext.asyncio import AsyncSession
from app.models import History, Log
from app import constants


async def generate_import(session: AsyncSession, log: Log):
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
