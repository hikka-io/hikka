from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
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
        select(Character).filter(Character.slug == slug.lower())
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
