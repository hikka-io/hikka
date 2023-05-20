from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.models import Anime
from typing import Union


async def get_anime_info_by_slug(
    session: AsyncSession, slug: str
) -> Union[Anime, None]:
    return await session.scalar(
        select(Anime)
        .filter_by(slug=slug)
        .options(
            selectinload(Anime.producers),
            selectinload(Anime.studios),
            selectinload(Anime.genres),
        )
    )
