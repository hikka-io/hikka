from sqlalchemy import select, func, exists, ScalarResult, Select
from app.common.service.sort import build_manga_order_by
from app.common.schemas.manga import MangaSearchArgs
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from app.service import manga_search_filter
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


def manga_exclude_read_filter(
    search: MangaSearchArgs, query: Select, request_user: User | None
):
    if not request_user or not search.exclude_read_status:
        return query

    return query.filter(
        ~exists().where(
            MangaRead.deleted == False,  # noqa: E712
            MangaRead.status.in_(search.exclude_read_status),
            MangaRead.user_id == request_user.id,
            MangaRead.content_id == Manga.id,
        )
    )


async def manga_exclude_content_ids(
    session: AsyncSession, search: MangaSearchArgs, request_user: User | None
) -> list[str]:
    if not request_user or not search.exclude_read_status:
        return []

    content_ids = await session.scalars(
        select(Manga.content_id)
        .join(MangaRead, MangaRead.content_id == Manga.id)
        .filter(
            MangaRead.user_id == request_user.id,
            MangaRead.status.in_(search.exclude_read_status),
            MangaRead.deleted == False,  # noqa: E712
        )
    )

    return content_ids.all()


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
    query = manga_exclude_read_filter(search, query, request_user)

    query = query.order_by(*build_manga_order_by(search.sort))

    query = query.options(*load_options)
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def manga_search_total(
    session: AsyncSession,
    search: MangaSearchArgs,
    filter_ids: list[str],
    request_user: User | None,
):
    query = select(func.count(Manga.id)).filter(Manga.deleted == False)  # noqa: E712

    if filter_ids:
        query = query.filter(Manga.content_id.in_(filter_ids))

    # NOTE: we should have dedicated nsfw filter
    # and don't do stupid things like this
    hide_nsfw = len(filter_ids) == 0

    query = manga_search_filter(search, query, hide_nsfw)
    query = manga_exclude_read_filter(search, query, request_user)

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
