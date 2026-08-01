from app.common.service.sort import build_manga_order_by
from sqlalchemy import select, func, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from app.service import manga_search_filter
from app.schemas import MangaSearchArgs
from sqlalchemy.orm import joinedload

from app.models import (
    MangaCharacter,
    MangaAuthor,
    MangaRead,
    Manga,
    User,
)


async def get_manga_info_by_slug(
    session: AsyncSession, slug: str
) -> Manga | None:
    return await session.scalar(
        select(Manga)
        .filter(
            Manga.slug == slug.lower(),
            Manga.deleted == False,  # noqa: E712
        )
        .options(
            joinedload(Manga.authors).joinedload(MangaAuthor.person),
            joinedload(Manga.magazines),
            joinedload(Manga.genres),
        )
    )


async def get_manga_by_slug(session: AsyncSession, slug: str) -> Manga | None:
    return await session.scalar(
        select(Manga).filter(
            Manga.slug == slug.lower(),
            Manga.deleted == False,  # noqa: E712
        )
    )


async def manga_search(
    session: AsyncSession,
    search: MangaSearchArgs,
    filter_ids: list[str],
    request_user: User | None,
    limit: int,
    offset: int,
):
    # Load request user read statuses here
    load_options = [
        joinedload(Manga.read),
        with_loader_criteria(
            MangaRead,
            MangaRead.user_id == request_user.id if request_user else None,
        ),
    ]

    query = select(Manga).filter(Manga.deleted == False)  # noqa: E712

    if filter_ids:
        query = query.filter(Manga.content_id.in_(filter_ids))

    # NOTE: we should have dedicated nsfw filter
    # and don't do stupid things like this
    hide_nsfw = len(filter_ids) == 0

    query = manga_search_filter(search, query, hide_nsfw)

    query = query.order_by(*build_manga_order_by(search.sort))

    query = query.options(*load_options)
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def manga_search_total(
    session: AsyncSession,
    search: MangaSearchArgs,
    filter_ids: list[str],
):
    query = select(func.count(Manga.id)).filter(Manga.deleted == False)  # noqa: E712

    if filter_ids:
        query = query.filter(Manga.content_id.in_(filter_ids))

    query = manga_search_filter(search, query)

    return await session.scalar(query)


async def manga_characters_count(session: AsyncSession, manga: Manga) -> int:
    return await session.scalar(
        select(func.count(MangaCharacter.id)).filter(
            MangaCharacter.manga == manga
        )
    )


async def manga_characters(
    session: AsyncSession, manga: Manga, limit: int, offset: int
) -> ScalarResult[MangaCharacter]:
    return await session.scalars(
        select(MangaCharacter)
        .filter(MangaCharacter.manga == manga)
        .options(joinedload(MangaCharacter.character))
        .limit(limit)
        .offset(offset)
    )
