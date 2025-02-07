from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Image
from app import constants


async def get_images(session: AsyncSession, urls: list[str]) -> list[Image]:
    paths = [url.replace(constants.CDN_ENDPOINT, "") for url in urls]
    return await session.scalars(select(Image).filter(Image.path.in_(paths)))
