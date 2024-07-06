from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import Moderation
# from datetime import datetime
# from uuid import UUID


async def get_moderation(
    session: AsyncSession,
    # content_type: str,
    # content_id: UUID,
    # user_id: UUID,
    # threshold: datetime,
):
    return await session.scalar(
        select(Moderation)
        # .filter(
        #     Moderation.content_type == content_type,
        #     Moderation.content_id == content_id,
        #     Moderation.user_id == user_id,
        #     Moderation.created > threshold,
        # )
        .order_by(desc(Moderation.created))
    )
