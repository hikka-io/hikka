from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import History
from datetime import datetime
from uuid import UUID


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
        .order_by(
            desc(History.updated),
            desc(History.created),
        )
    )


async def get_latest_history(
    session: AsyncSession,
    user_id: UUID,
):
    return await session.scalar(
        select(History)
        .filter(History.user_id == user_id)
        .order_by(desc(History.updated))
        .limit(1)
    )
