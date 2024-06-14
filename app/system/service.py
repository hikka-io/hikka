from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.models import Image


async def get_images_count(session: AsyncSession):
    return await session.scalar(
        select(func.count(Image.id)).filter(
            Image.uploaded == True  # noqa: E712
        )
    )


async def get_images(session: AsyncSession, limit: int, offset: int):
    return await session.scalars(
        select(Image)
        .filter(Image.uploaded == True)  # noqa: E712
        .order_by(desc(Image.created))
        .limit(limit)
        .offset(offset)
    )
