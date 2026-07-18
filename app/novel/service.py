from app.common.service.sort import build_novel_order_by
from sqlalchemy import select, func, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from app.service import novel_search_filter
from app.schemas import NovelSearchArgs
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload


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
            Novel.slug == slug.lower(),
            Novel.deleted == False,  # noqa: E712
        )
        .options(
            joinedload(Novel.authors).joinedload(NovelAuthor.person),
            joinedload(Novel.magazines),
            joinedload(Novel.genres),
        )
    )


async def get_novel_by_slug(session: AsyncSession, slug: str) -> Novel | None:
    return await session.scalar(
        select(Novel).filter(
            Novel.slug == slug.lower(),
            Novel.deleted == False,  # noqa: E712
        )
    )


async def novel_search(
    session: AsyncSession,
    search: NovelSearchArgs,
    filter_ids: list[str],
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
        selectinload(Novel.genres),
        selectinload(Novel.magazines),
    ]

    query = select(Novel).filter(Novel.deleted == False)  # noqa: E712

    if filter_ids:
        query = query.filter(Novel.content_id.in_(filter_ids))

    query = novel_search_filter(search, query)

    query = query.order_by(*build_novel_order_by(search.sort))

    query = query.options(*load_options)
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def novel_search_total(
    session: AsyncSession,
    search: NovelSearchArgs,
    filter_ids: list[str],
):
    query = select(func.count(Novel.id)).filter(Novel.deleted == False) # noqa: E712

    if filter_ids:
        query = query.filter(Novel.content_id.in_(filter_ids))

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
