from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.orm import with_expression
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload
from .schemas import AnimeSearchArgs
from sqlalchemy import func
from app import constants

from app.service import (
    get_comments_count_subquery,
    anime_search_filter,
    build_order_by,
)

from app.models import (
    AnimeRecommendation,
    AnimeCharacter,
    CompanyAnime,
    AnimeEpisode,
    AnimeStaff,
    AnimeWatch,
    Company,
    Person,
    Genre,
    Anime,
    User,
)


async def get_anime_info_by_slug(
    session: AsyncSession, slug: str
) -> Anime | None:
    return await session.scalar(
        select(Anime)
        .filter(
            func.lower(Anime.slug) == slug.lower(),
            Anime.deleted == False,  # noqa: E712
        )
        .options(
            selectinload(Anime.companies).selectinload(CompanyAnime.company),
            selectinload(Anime.genres),
        )
        .options(
            with_expression(
                Anime.comments_count,
                get_comments_count_subquery(Anime.id, constants.CONTENT_ANIME),
            )
        )
    )


async def anime_characters(
    session: AsyncSession, anime: Anime, limit: int, offset: int
) -> list[AnimeCharacter]:
    return await session.scalars(
        select(AnimeCharacter)
        .filter(AnimeCharacter.anime == anime)
        .options(selectinload(AnimeCharacter.character))
        .limit(limit)
        .offset(offset)
    )


async def anime_staff(
    session: AsyncSession, anime: Anime, limit: int, offset: int
) -> list[AnimeStaff]:
    return await session.scalars(
        select(AnimeStaff)
        .join(Person, AnimeStaff.person)
        .filter(AnimeStaff.anime == anime)
        .options(joinedload(AnimeStaff.person))
        .options(joinedload(AnimeStaff.roles))
        .order_by(desc(AnimeStaff.weight), asc(Person.name_en))
        .limit(limit)
        .offset(offset)
    )


async def anime_episodes_count(session: AsyncSession, anime: Anime) -> int:
    return await session.scalar(
        select(func.count(AnimeEpisode.id)).filter(AnimeEpisode.anime == anime)
    )


async def anime_episodes(
    session: AsyncSession, anime: Anime, limit: int, offset: int
) -> list[AnimeStaff]:
    return await session.scalars(
        select(AnimeEpisode)
        .filter(AnimeEpisode.anime == anime)
        .order_by(AnimeEpisode.index)
        .limit(limit)
        .offset(offset)
    )


async def anime_staff_count(session: AsyncSession, anime: Anime) -> int:
    return await session.scalar(
        select(func.count(AnimeStaff.id)).filter(AnimeStaff.anime == anime)
    )


async def franchise_count(session: AsyncSession, anime: Anime) -> int:
    return await session.scalar(
        select(func.count(Anime.id)).filter(
            Anime.franchise_id == anime.franchise_id,
            Anime.deleted == False,  # noqa: E712
        )
    )


async def franchise(
    session: AsyncSession,
    anime: Anime,
    request_user: User | None,
    limit: int,
    offset: int,
):
    # Load request user watch statuses here
    load_options = [
        joinedload(Anime.watch),
        with_loader_criteria(
            AnimeWatch,
            AnimeWatch.user_id == request_user.id if request_user else None,
        ),
    ]

    return await session.scalars(
        select(Anime)
        .filter(
            Anime.franchise_id == anime.franchise_id,
            Anime.deleted == False,  # noqa: E712
        )
        .order_by(desc(Anime.start_date))
        .options(*load_options)
        .limit(limit)
        .offset(offset)
    )


async def anime_recommendations(
    session: AsyncSession,
    anime: Anime,
    request_user: User | None,
    limit: int,
    offset: int,
) -> list[AnimeRecommendation]:
    # Load request user watch statuses here
    load_options = [
        joinedload(Anime.watch),
        with_loader_criteria(
            AnimeWatch,
            AnimeWatch.user_id == request_user.id if request_user else None,
        ),
    ]

    return await session.scalars(
        select(Anime)
        .join(
            AnimeRecommendation,
            AnimeRecommendation.recommendation_id == Anime.id,
        )
        .filter(
            AnimeRecommendation.anime == anime,
            Anime.deleted == False,  # noqa: E712
        )
        .order_by(desc(AnimeRecommendation.weight))
        .options(*load_options)
        .limit(limit)
        .offset(offset)
    )


async def anime_recommendations_count(
    session: AsyncSession, anime: Anime
) -> int:
    return await session.scalar(
        select(func.count(AnimeRecommendation.id)).filter(
            AnimeRecommendation.anime == anime
        )
    )


async def anime_characters_count(session: AsyncSession, anime: Anime) -> int:
    return await session.scalar(
        select(func.count(AnimeCharacter.id)).filter(
            AnimeCharacter.anime == anime
        )
    )


async def company_count(session: AsyncSession, slugs: list[str]):
    return await session.scalar(
        select(func.count(Company.id)).filter(Company.slug.in_(slugs))
    )


async def anime_genre_count(session: AsyncSession, slugs: list[str]):
    return await session.scalar(
        select(func.count(Genre.id)).filter(Genre.slug.in_(slugs))
    )


async def anime_search(
    session: AsyncSession,
    search: AnimeSearchArgs,
    request_user: User | None,
    limit: int,
    offset: int,
):
    # Load request user watch statuses here
    load_options = [
        joinedload(Anime.watch),
        with_loader_criteria(
            AnimeWatch,
            AnimeWatch.user_id == request_user.id if request_user else None,
        ),
    ]

    query = select(Anime).filter(Anime.deleted == False)  # noqa: E712
    query = anime_search_filter(search, query)

    query = query.order_by(*build_order_by(search.sort))

    query = query.options(*load_options)
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def anime_search_total(session: AsyncSession, search: AnimeSearchArgs):
    query = select(func.count(Anime.id)).filter(
        Anime.deleted == False,  # noqa: E712
    )

    query = anime_search_filter(search, query)

    return await session.scalar(query)


async def anime_genres(session: AsyncSession):
    return await session.scalars(select(Genre).order_by(Genre.slug))


# I hate this function so much
# But we need it for having watch satatuses in Meilisearch results
async def anime_meilisearch_watch(
    session: AsyncSession,
    search: AnimeSearchArgs,
    request_user: User | None,
    meilisearch_result: dict,
):
    slugs = [anime["slug"] for anime in meilisearch_result["list"]]

    # Load request user watch statuses here
    load_options = [
        joinedload(Anime.watch),
        with_loader_criteria(
            AnimeWatch,
            AnimeWatch.user_id == request_user.id if request_user else None,
        ),
    ]

    query = select(Anime).filter(Anime.slug.in_(slugs)).options(*load_options)

    if len(search.sort) > 0:
        query = query.order_by(*build_order_by(search.sort))

    anime_list = await session.scalars(query)
    meilisearch_result["list"] = anime_list.unique().all()

    # Results must be sorted here to ensure same order as Meilisearch results
    meilisearch_result["list"] = sorted(
        meilisearch_result["list"], key=lambda x: slugs.index(x.slug)
    )

    return meilisearch_result
