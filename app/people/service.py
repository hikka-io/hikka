from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_expression
from app.service import anime_loadonly
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc
from sqlalchemy import func

from app.models import (
    MangaAuthor,
    NovelAuthor,
    AnimeStaff,
    AnimeVoice,
    AnimeWatch,
    MangaRead,
    NovelRead,
    Person,
    Anime,
    Manga,
    Novel,
    User,
)


async def get_person_by_slug(session: AsyncSession, slug: str) -> Person | None:
    return await session.scalar(
        select(Person)
        .filter(func.lower(Person.slug) == slug.lower())
        .options(
            with_expression(
                Person.anime_count,
                select(func.count(AnimeStaff.id))
                .filter(AnimeStaff.person_id == Person.id)
                .join(Anime)
                .filter(Anime.deleted == False)  # noqa: E712
                .scalar_subquery(),
            )
        )
        .options(
            with_expression(
                Person.characters_count,
                select(func.count(AnimeVoice.id))
                .filter(AnimeVoice.person_id == Person.id)
                .join(Anime)
                .filter(Anime.deleted == False)  # noqa: E712
                .scalar_subquery(),
            )
        )
    )


async def search_total(session: AsyncSession):
    return await session.scalar(select(func.count(Person.id)))


async def people_search(
    session: AsyncSession,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(Person)
        .order_by(
            desc(Person.favorites),
            desc(Person.content_id),
        )
        .limit(limit)
        .offset(offset)
    )


async def person_anime_total(session: AsyncSession, person: Person):
    return await session.scalar(
        select(func.count(AnimeStaff.id))
        .filter(AnimeStaff.person == person)
        .join(Anime)
        .filter(Anime.deleted == False)  # noqa: E712
    )


async def person_anime(
    session: AsyncSession,
    person: Person,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(AnimeStaff)
        .filter(AnimeStaff.person == person)
        .join(Anime)
        .filter(Anime.deleted == False)  # noqa: E712
        .options(
            anime_loadonly(joinedload(AnimeStaff.anime)).joinedload(
                Anime.watch
            ),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        )
        .order_by(
            desc(Anime.score),
            desc(Anime.scored_by),
            desc(Anime.content_id),
        )
        .limit(limit)
        .offset(offset)
    )


async def person_manga_total(session: AsyncSession, person: Person):
    return await session.scalar(
        select(func.count(MangaAuthor.id))
        .filter(MangaAuthor.person == person)
        .join(Manga)
        .filter(Manga.deleted == False)  # noqa: E712
    )


async def person_manga(
    session: AsyncSession,
    person: Person,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(MangaAuthor)
        .filter(MangaAuthor.person == person)
        .join(Manga)
        .filter(Manga.deleted == False)  # noqa: E712
        .options(
            joinedload(MangaAuthor.manga).joinedload(Manga.read),
            with_loader_criteria(
                MangaRead,
                MangaRead.user_id == request_user.id if request_user else None,
            ),
        )
        .order_by(
            desc(Manga.score),
            desc(Manga.scored_by),
            desc(Manga.content_id),
        )
        .limit(limit)
        .offset(offset)
    )


async def person_novel_total(session: AsyncSession, person: Person):
    return await session.scalar(
        select(func.count(NovelAuthor.id))
        .filter(NovelAuthor.person == person)
        .join(Novel)
        .filter(Novel.deleted == False)  # noqa: E712
    )


async def person_novel(
    session: AsyncSession,
    person: Person,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(NovelAuthor)
        .filter(NovelAuthor.person == person)
        .join(Novel)
        .filter(Novel.deleted == False)  # noqa: E712
        .options(
            joinedload(NovelAuthor.novel).joinedload(Novel.read),
            with_loader_criteria(
                NovelRead,
                NovelRead.user_id == request_user.id if request_user else None,
            ),
        )
        .order_by(
            desc(Novel.score),
            desc(Novel.scored_by),
            desc(Novel.content_id),
        )
        .limit(limit)
        .offset(offset)
    )


async def person_voices_total(session: AsyncSession, person: Person):
    return await session.scalar(
        select(func.count(AnimeVoice.id))
        .filter(AnimeVoice.person == person)
        .join(Anime)
        .filter(Anime.deleted == False)  # noqa: E712
    )


async def person_voices(
    session: AsyncSession,
    person: Person,
    request_user: User | None,
    limit: int,
    offset: int,
):
    return await session.scalars(
        select(AnimeVoice)
        .filter(AnimeVoice.person == person)
        .options(
            anime_loadonly(joinedload(AnimeVoice.anime)).joinedload(
                Anime.watch
            ),
            with_loader_criteria(
                AnimeWatch,
                AnimeWatch.user_id == request_user.id if request_user else None,
            ),
        )
        .options(joinedload(AnimeVoice.character))
        .join(Anime)
        .filter(Anime.deleted == False)  # noqa: E712
        .order_by(
            desc(Anime.score),
            desc(Anime.scored_by),
            desc(Anime.content_id),
        )
        .limit(limit)
        .offset(offset)
    )
