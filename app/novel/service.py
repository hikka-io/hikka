from sqlalchemy import select, func, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.orm import with_expression
from .utils import build_novel_filters_ms
from app.schemas import NovelSearchArgs
from sqlalchemy.orm import joinedload
from app import meilisearch
from app import constants

from app.service import (
    get_comments_count_subquery,
    build_novel_order_by,
    novel_search_filter,
)

from app.models import (
    NovelCharacter,
    NovelAuthor,
    NovelRead,
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


async def novel_search(
    session: AsyncSession,
    search: NovelSearchArgs,
    request_user: User | None,
    limit: int,
    offset: int,
):
    # Load request user read statuses here
    load_options = [
        joinedload(Novel.read),
        with_loader_criteria(
            NovelRead,
            NovelRead.user_id == request_user.id if request_user else None,
        ),
    ]

    query = select(Novel).filter(Novel.deleted == False)  # noqa: E712
    query = novel_search_filter(search, query)

    query = query.order_by(*build_novel_order_by(search.sort))

    query = query.options(*load_options)
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
) -> ScalarResult[NovelCharacter]:
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

    # Load request user read statuses here
    load_options = [
        joinedload(Novel.read),
        with_loader_criteria(
            NovelRead,
            NovelRead.user_id == request_user.id if request_user else None,
        ),
    ]

    query = select(Novel).filter(Novel.slug.in_(slugs)).options(*load_options)

    if len(search.sort) > 0:
        query = query.order_by(*build_novel_order_by(search.sort))

    novel_list = await session.scalars(query)
    meilisearch_result["list"] = novel_list.unique().all()

    # Results must be sorted here to ensure same order as Meilisearch results
    meilisearch_result["list"] = sorted(
        meilisearch_result["list"], key=lambda x: slugs.index(x.slug)
    )

    return meilisearch_result
