from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.orm import with_expression
from .utils import build_manga_filters_ms
from app.schemas import MangaSearchArgs
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func
from app import meilisearch
from app import constants
import random

from app.service import (
    get_comments_count_subquery,
    build_manga_order_by,
    manga_search_filter,
)

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


async def manga_search(
    session: AsyncSession,
    search: MangaSearchArgs,
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
    query = manga_search_filter(search, query)

    query = query.order_by(*build_manga_order_by(search.sort))

    query = query.options(*load_options)
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


async def manga_search_query(
    session: AsyncSession,
    search: MangaSearchArgs,
    request_user: User | None,
    page: int,
    size: int,
):
    meilisearch_result = await meilisearch.search(
        constants.SEARCH_INDEX_MANGA,
        filter=build_manga_filters_ms(search),
        query=search.query,
        sort=search.sort,
        page=page,
        size=size,
    )

    slugs = [manga["slug"] for manga in meilisearch_result["list"]]

    # Load request user read statuses here
    load_options = [
        joinedload(Manga.read),
        with_loader_criteria(
            MangaRead,
            MangaRead.user_id == request_user.id if request_user else None,
        ),
    ]

    query = select(Manga).filter(Manga.slug.in_(slugs)).options(*load_options)

    if len(search.sort) > 0:
        query = query.order_by(*build_manga_order_by(search.sort))

    manga_list = await session.scalars(query)
    meilisearch_result["list"] = manga_list.unique().all()

    # Results must be sorted here to ensure same order as Meilisearch results
    meilisearch_result["list"] = sorted(
        meilisearch_result["list"], key=lambda x: slugs.index(x.slug)
    )

    return meilisearch_result


async def random_manga(session: AsyncSession):
    manga_ids = await session.scalars(select(Manga.id))
    manga = await session.scalar(
        select(Manga).filter(Manga.id == random.choice(manga_ids.all()))
    )
    return await get_manga_info_by_slug(session, manga.slug)

