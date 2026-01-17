from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Genre


async def get_genres(session: AsyncSession):
    return await session.scalars(
        select(Genre).order_by(Genre.name_ua.asc(), Genre.slug)
    )
