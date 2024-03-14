from sqlalchemy.ext.asyncio import AsyncSession
from app.service import anime_loadonly
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc
from sqlalchemy import func

from app.models import (
    AnimeCharacter,
    AnimeVoice,
    Character,
    Anime,
)


async def get_character_by_slug(
    session: AsyncSession, slug: str
) -> Character | None:
    return await session.scalar(
        select(Character).filter(func.lower(Character.slug) == slug.lower())
    )


async def search_total(session: AsyncSession):
    return await session.scalar(select(func.count(Character.id)))


async def characters_search(
    session: AsyncSession,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(Character)
        .order_by(desc("favorites"), desc("content_id"))
        .limit(limit)
        .offset(offset)
    )


async def character_anime_total(session: AsyncSession, character: Character):
    return await session.scalar(
        select(func.count(AnimeCharacter.id)).filter(
            AnimeCharacter.character == character
        )
    )


async def character_anime(
    session: AsyncSession,
    character: Character,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(AnimeCharacter)
        .filter(AnimeCharacter.character == character)
        .join(Anime)
        .options(anime_loadonly(joinedload(AnimeCharacter.anime)))
        .order_by(
            desc(Anime.score), desc(Anime.scored_by), desc(Anime.content_id)
        )
        .limit(limit)
        .offset(offset)
    )


async def character_voices_total(session: AsyncSession, character: Character):
    return await session.scalar(
        select(func.count(AnimeVoice.id)).filter(
            AnimeVoice.character == character
        )
    )


async def character_voices(
    session: AsyncSession,
    character: Character,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(AnimeVoice)
        .filter(AnimeVoice.character == character)
        .join(Anime)
        .options(anime_loadonly(joinedload(AnimeVoice.anime)))
        .options(joinedload(AnimeVoice.person))
        .order_by(
            desc(Anime.score),
            desc(Anime.scored_by),
            desc(Anime.content_id),
        )
        .limit(limit)
        .offset(offset)
    )
