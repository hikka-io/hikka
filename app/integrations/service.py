from app.models import Anime, AnimeCharacter, Character
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID


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
