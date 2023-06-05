from app.models import Character, AnimeCharacter, Anime, Person
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import anime_loadonly
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc
from sqlalchemy import func
from typing import Union


async def get_person_by_slug(
    session: AsyncSession, slug: str
) -> Union[Person, None]:
    return await session.scalar(select(Person).filter_by(slug=slug))


async def search_total(session: AsyncSession):
    return await session.scalar(select(func.count(Character.id)))


async def people_search(
    session: AsyncSession,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(Person)
        .order_by(desc("favorites"), desc("content_id"))
        .limit(limit)
        .offset(offset)
    )
