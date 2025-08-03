from .schemas import MALContentArgs, MALContentTypeEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import asc, desc, select, text
from sqlalchemy.orm import joinedload
from app import constants

from app.models import (
    AnimeCharacter,
    AnimeStaff,
    Character,
    Person,
    Anime,
    Manga,
    Novel,
)


def get_content_model(content_type: MALContentTypeEnum):
    match content_type:
        case constants.CONTENT_ANIME:
            return Anime
        case constants.CONTENT_MANGA:
            return Manga
        case constants.CONTENT_NOVEL:
            return Novel


async def get_content_by_mal_id(
    session: AsyncSession, content_type: MALContentTypeEnum, mal_id: int
) -> Anime | Manga | Novel | None:
    model_class = get_content_model(content_type)

    return await session.scalar(
        select(model_class).filter(
            model_class.mal_id == mal_id,
            model_class.deleted == False,  # noqa: E712
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
    session: AsyncSession,
    content_type: MALContentTypeEnum,
    args: MALContentArgs,
) -> list[Anime | Manga | Novel | None]:
    model_class = get_content_model(content_type)

    query = select(model_class).filter(
        model_class.mal_id.in_(args.mal_ids),
        model_class.deleted == False,  # noqa: E712
    )

    content = await session.scalars(query)
    content_cache = {entry.mal_id: entry for entry in content}

    return [content_cache.get(mal_id) for mal_id in args.mal_ids]


async def get_anime_by_anitube(session: AsyncSession, anitube_id: int):
    anitube_url = f"https://anitube.in.ua/{anitube_id}-"

    return await session.scalar(
        select(Anime)
        .filter(
            # RIP performance (?)
            Anime.external.op("@?")(
                text(f"'$[*].url ? (@ starts with \"{anitube_url}\")'")
            ),
            Anime.deleted == False,  # noqa: E712
        )
        .order_by(
            desc(Anime.score),
            desc(Anime.scored_by),
            desc(Anime.content_id),
        )
    )
