from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_expression
from app.service import anime_loadonly
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc
from sqlalchemy import func

from app.models import (
    AnimeCharacter,
    MangaCharacter,
    NovelCharacter,
    AnimeVoice,
    AnimeWatch,
    MangaRead,
    NovelRead,
    Character,
    Anime,
    Manga,
    Novel,
    User,
)


async def get_character_by_slug(
    session: AsyncSession, slug: str
) -> Character | None:
    return await session.scalar(
        select(Character)
        .filter(func.lower(Character.slug) == slug.lower())
        .options(
            with_expression(
                Character.anime_count,
                select(func.count(AnimeCharacter.id))
                .filter(AnimeCharacter.character_id == Character.id)
                .join(Anime)
                .filter(Anime.deleted == False)  # noqa: E712
                .scalar_subquery(),
            )
        )
        .options(
            with_expression(
                Character.voices_count,
                select(func.count(AnimeVoice.id))
                .filter(AnimeVoice.character_id == Character.id)
                .join(Anime)
                .filter(Anime.deleted == False)  # noqa: E712
                .scalar_subquery(),
            )
        )
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
        select(func.count(AnimeCharacter.id))
        .filter(AnimeCharacter.character == character)
        .join(Anime)
        .filter(Anime.deleted == False)  # noqa: E712
    )


async def character_anime(
    session: AsyncSession,
    character: Character,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(AnimeCharacter)
        .filter(AnimeCharacter.character == character)
        .join(Anime)
        .filter(Anime.deleted == False)  # noqa: E712
        .options(
            anime_loadonly(joinedload(AnimeCharacter.anime)).joinedload(
                Anime.watch
            ),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        )
        .order_by(
            desc(Anime.score), desc(Anime.scored_by), desc(Anime.content_id)
        )
        .limit(limit)
        .offset(offset)
    )


async def character_manga_total(session: AsyncSession, character: Character):
    return await session.scalar(
        select(func.count(MangaCharacter.id))
        .filter(MangaCharacter.character == character)
        .join(Manga)
        .filter(Manga.deleted == False)  # noqa: E712
    )


async def character_manga(
    session: AsyncSession,
    character: Character,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(MangaCharacter)
        .filter(MangaCharacter.character == character)
        .join(Manga)
        .filter(Manga.deleted == False)  # noqa: E712
        .options(
            joinedload(MangaCharacter.manga).joinedload(Manga.read),
            with_loader_criteria(
                MangaRead,
                MangaRead.user_id == request_user.id if request_user else None,
            ),
        )
        .order_by(
            desc(Manga.score), desc(Manga.scored_by), desc(Manga.content_id)
        )
        .limit(limit)
        .offset(offset)
    )


async def character_novel_total(session: AsyncSession, character: Character):
    return await session.scalar(
        select(func.count(NovelCharacter.id))
        .filter(NovelCharacter.character == character)
        .join(Novel)
        .filter(Novel.deleted == False)  # noqa: E712
    )


async def character_novel(
    session: AsyncSession,
    character: Character,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(NovelCharacter)
        .filter(NovelCharacter.character == character)
        .join(Novel)
        .filter(Novel.deleted == False)  # noqa: E712
        .options(
            joinedload(NovelCharacter.novel).joinedload(Novel.read),
            with_loader_criteria(
                NovelRead,
                NovelRead.user_id == request_user.id if request_user else None,
            ),
        )
        .order_by(
            desc(Novel.score), desc(Novel.scored_by), desc(Novel.content_id)
        )
        .limit(limit)
        .offset(offset)
    )


async def character_voices_total(session: AsyncSession, character: Character):
    return await session.scalar(
        select(func.count(AnimeVoice.id))
        .filter(AnimeVoice.character == character)
        .join(Anime)
        .filter(Anime.deleted == False)  # noqa: E712
    )


async def character_voices(
    session: AsyncSession,
    character: Character,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(AnimeVoice)
        .filter(AnimeVoice.character == character)
        .join(Anime)
        .filter(Anime.deleted == False)  # noqa: E712
        # .options(anime_loadonly(joinedload(AnimeVoice.anime)))
        .options(
            anime_loadonly(joinedload(AnimeVoice.anime)).joinedload(
                Anime.watch
            ),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        )
        .options(joinedload(AnimeVoice.person))
        .order_by(
            desc(Anime.score),
            desc(Anime.scored_by),
            desc(Anime.content_id),
        )
        .limit(limit)
        .offset(offset)
    )
