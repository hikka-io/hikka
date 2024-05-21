from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import joinedload
from .schemas import MALAnimeArgs

from app.models import (
    AnimeCharacter,
    AnimeStaff,
    Character,
    Person,
    Anime,
)


async def get_anime_by_mal_id(
    session: AsyncSession, mal_id: int
) -> Anime | None:
    return await session.scalar(
        select(Anime).filter(
            Anime.mal_id == mal_id,
            Anime.deleted == False,  # noqa: E712
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


async def get_by_mal_ids(
    session: AsyncSession, args: MALAnimeArgs
) -> list[Anime | None]:
    query = select(Anime).filter(
        Anime.mal_id.in_(args.mal_ids),
        Anime.deleted == False,  # noqa: E712
    )
    anime = await session.scalars(query)
    anime_cache = {entry.mal_id: entry for entry in anime}
    return [anime_cache.get(mal_id) for mal_id in args.mal_ids]
