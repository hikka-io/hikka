from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import joinedload
from uuid import UUID

from app.models import (
    AnimeCharacter,
    AnimeStaff,
    Character,
    Person,
    Anime,
)


async def get_anime_by_watari(session: AsyncSession, slug: UUID):
    watari_url = f"https://www.watari-anime.com/watch?wid={slug}"
    return await session.scalar(
        select(Anime)
        .filter(Anime.external.op("@>")([{"url": watari_url}]))
        .order_by(
            desc(Anime.score), desc(Anime.scored_by), desc(Anime.content_id)
        )
    )


async def get_main_characters(
    session: AsyncSession, anime: Anime
) -> list[Character]:
    return await session.scalars(
        select(Character)
        .join(
            AnimeCharacter,
            AnimeCharacter.character_id == Character.id,
        )
        .filter(
            AnimeCharacter.anime == anime,
            AnimeCharacter.main == True,  # noqa: E712
        )
        .order_by(desc(Character.favorites), desc(Character.id))
    )


async def get_anime_main_staff(
    session: AsyncSession, anime: Anime
) -> list[AnimeStaff]:
    return await session.scalars(
        select(AnimeStaff)
        .join(Person, AnimeStaff.person)
        .filter(AnimeStaff.anime == anime)
        .options(joinedload(AnimeStaff.person))
        .options(joinedload(AnimeStaff.roles))
        .order_by(desc(AnimeStaff.weight), asc(Person.name_en))
        .limit(8)
    )
