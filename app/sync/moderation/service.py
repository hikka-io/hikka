from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import Moderation, Edit
from datetime import datetime
from uuid import UUID


async def get_moderation(
    session: AsyncSession,
    user_id: UUID,
    log_id: UUID,
    target_type: str | None = None,
):
    query = select(Moderation).filter(
        Moderation.user_id == user_id,
        Moderation.log_id == log_id,
    )

    if target_type:
        query = query.filter(
            Moderation.target_type == target_type,
        )

    return await session.scalar(query.order_by(desc(Moderation.created)))


async def get_edit(session, content_id):
    return await session.scalar(select(Edit).filter(Edit.id == content_id))
