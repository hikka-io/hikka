from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from app.models import UserEditStats


async def get_edits_top_count(session: AsyncSession):
    return await session.scalar(select(func.count(UserEditStats.id)))


async def get_edits_top(session: AsyncSession, limit: int, offset: int):
    return await session.scalars(
        select(UserEditStats)
        .options(joinedload(UserEditStats.user))
        .order_by(desc(UserEditStats.accepted))
    )
