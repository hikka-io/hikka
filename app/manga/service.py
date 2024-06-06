from app.service import get_comments_count_subquery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import with_expression
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import joinedload
from .schemas import MangaSearchArgs
from sqlalchemy import func
from app import constants

from app.models import (
    MangaCharacter,
    MangaAuthor,
    Genre,
    Manga,
    User,
)


async def get_manga_info_by_slug(
    session: AsyncSession, slug: str
) -> Manga | None:
    return await session.scalar(
        select(Manga)
        .filter(
            func.lower(Manga.slug) == slug.lower(),
            Manga.deleted == False,  # noqa: E712
        )
        .options(
            joinedload(Manga.authors).joinedload(MangaAuthor.person),
            joinedload(Manga.magazines),
            joinedload(Manga.genres),
        )
        .options(
            with_expression(
                Manga.comments_count,
                get_comments_count_subquery(Manga.id, constants.CONTENT_MANGA),
            )
        )
    )


async def get_manga_by_slug(session: AsyncSession, slug: str) -> Manga | None:
    return await session.scalar(
        select(Manga).filter(
            func.lower(Manga.slug) == slug.lower(),
            Manga.deleted == False,  # noqa: E712
        )
    )


def build_manga_order_by(sort: list[str]):
    order_mapping = {
        "scored_by": Manga.scored_by,
        "score": Manga.score,
    }

    order_by = [
        (
            desc(order_mapping[field])
            if order == "desc"
            else asc(order_mapping[field])
        )
        for field, order in (entry.split(":") for entry in sort)
    ] + [desc(Manga.content_id)]

    return order_by


def manga_search_filter(
    search: MangaSearchArgs,
    query: Select,
    hide_nsfw=True,
):
    # All genres must be present in query result
    if len(search.genres) > 0:
        query = query.filter(
            and_(
                *[
                    Manga.genres.any(Genre.slug == slug)
                    for slug in search.genres
                ]
            )
        )

    return query


async def manga_search(
    session: AsyncSession,
    search: MangaSearchArgs,
    request_user: User | None,
    limit: int,
    offset: int,
):
    query = select(Manga).filter(Manga.deleted == False)  # noqa: E712
    query = manga_search_filter(search, query)

    query = query.order_by(*build_manga_order_by(search.sort))

    # query = query.options(*load_options)
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def manga_search_total(session: AsyncSession, search: MangaSearchArgs):
    query = select(func.count(Manga.id)).filter(
        Manga.deleted == False,  # noqa: E712
    )

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
) -> list[MangaCharacter]:
    return await session.scalars(
        select(MangaCharacter)
        .filter(MangaCharacter.manga == manga)
        .options(joinedload(MangaCharacter.character))
        .limit(limit)
        .offset(offset)
    )
