from app.service import get_comments_count_subquery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import with_expression
from .utils import build_novel_filters_ms
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import joinedload
from .schemas import NovelSearchArgs
from sqlalchemy import func, and_
from app import meilisearch
from app import constants

from app.models import (
    NovelCharacter,
    NovelAuthor,
    Magazine,
    Genre,
    Novel,
    User,
)


async def get_novel_info_by_slug(
    session: AsyncSession, slug: str
) -> Novel | None:
    return await session.scalar(
        select(Novel)
        .filter(
            func.lower(Novel.slug) == slug.lower(),
            Novel.deleted == False,  # noqa: E712
        )
        .options(
            joinedload(Novel.authors).joinedload(NovelAuthor.person),
            joinedload(Novel.magazines),
            joinedload(Novel.genres),
        )
        .options(
            with_expression(
                Novel.comments_count,
                get_comments_count_subquery(Novel.id, constants.CONTENT_NOVEL),
            )
        )
    )


async def get_novel_by_slug(session: AsyncSession, slug: str) -> Novel | None:
    return await session.scalar(
        select(Novel).filter(
            func.lower(Novel.slug) == slug.lower(),
            Novel.deleted == False,  # noqa: E712
        )
    )


def build_novel_order_by(sort: list[str]):
    order_mapping = {
        "scored_by": Novel.scored_by,
        "score": Novel.score,
    }

    order_by = [
        (
            desc(order_mapping[field])
            if order == "desc"
            else asc(order_mapping[field])
        )
        for field, order in (entry.split(":") for entry in sort)
    ] + [desc(Novel.content_id)]

    return order_by


def novel_search_filter(
    search: NovelSearchArgs,
    query: Select,
    hide_nsfw=True,
):
    if search.score[0] and search.score[0] > 0:
        query = query.filter(Novel.score >= search.score[0])

    if search.score[1]:
        query = query.filter(Novel.score <= search.score[1])

    if len(search.status) > 0:
        query = query.filter(Novel.status.in_(search.status))

    if len(search.media_type) > 0:
        query = query.filter(Novel.media_type.in_(search.media_type))

    if search.only_translated:
        query = query.filter(Novel.translated_ua == True)  # noqa: E712

    if search.years[0]:
        query = query.filter(Novel.year >= search.years[0])

    if search.years[1]:
        query = query.filter(Novel.year <= search.years[1])

    if len(search.magazines) > 0:
        query = query.join(Novel.magazines).filter(
            Magazine.slug.in_(search.magazines)
        )

    # In some cases, like on front page, we would want to hide NSFW content
    if len(search.genres) == 0 and hide_nsfw:
        query = query.filter(
            and_(
                *[
                    ~Novel.genres.any(Genre.slug == slug)
                    for slug in ["ecchi", "erotica", "hentai"]
                ]
            )
        )

    # All genres must be present in query result
    if len(search.genres) > 0:
        query = query.filter(
            and_(
                *[
                    Novel.genres.any(Genre.slug == slug)
                    for slug in search.genres
                ]
            )
        )

    return query


async def novel_search(
    session: AsyncSession,
    search: NovelSearchArgs,
    request_user: User | None,
    limit: int,
    offset: int,
):
    query = select(Novel).filter(Novel.deleted == False)  # noqa: E712
    query = novel_search_filter(search, query)

    query = query.order_by(*build_novel_order_by(search.sort))

    # query = query.options(*load_options)
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def novel_search_total(session: AsyncSession, search: NovelSearchArgs):
    query = select(func.count(Novel.id)).filter(
        Novel.deleted == False,  # noqa: E712
    )

    query = novel_search_filter(search, query)

    return await session.scalar(query)


async def novel_characters_count(session: AsyncSession, novel: Novel) -> int:
    return await session.scalar(
        select(func.count(NovelCharacter.id)).filter(
            NovelCharacter.novel == novel
        )
    )


async def novel_characters(
    session: AsyncSession, novel: Novel, limit: int, offset: int
) -> list[NovelCharacter]:
    return await session.scalars(
        select(NovelCharacter)
        .filter(NovelCharacter.novel == novel)
        .options(joinedload(NovelCharacter.character))
        .limit(limit)
        .offset(offset)
    )


async def novel_search_query(
    session: AsyncSession,
    search: NovelSearchArgs,
    request_user: User | None,
    page: int,
    size: int,
):
    meilisearch_result = await meilisearch.search(
        constants.SEARCH_INDEX_NOVEL,
        filter=build_novel_filters_ms(search),
        query=search.query,
        sort=search.sort,
        page=page,
        size=size,
    )

    slugs = [novel["slug"] for novel in meilisearch_result["list"]]

    query = select(Novel).filter(Novel.slug.in_(slugs))

    if len(search.sort) > 0:
        query = query.order_by(*build_novel_order_by(search.sort))

    novel_list = await session.scalars(query)
    meilisearch_result["list"] = novel_list.unique().all()

    # Results must be sorted here to ensure same order as Meilisearch results
    meilisearch_result["list"] = sorted(
        meilisearch_result["list"], key=lambda x: slugs.index(x.slug)
    )

    return meilisearch_result
