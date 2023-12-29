from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy import select, desc, asc, and_
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload
from .schemas import AnimeSearchArgs
from sqlalchemy import func
from . import utils

from app.models import (
    AnimeRecommendation,
    AnimeCharacter,
    CompanyAnime,
    AnimeEpisode,
    AnimeGenre,
    AnimeStaff,
    AnimeWatch,
    Company,
    Person,
    Anime,
    User,
)


async def get_anime_info_by_slug(
    session: AsyncSession, slug: str
) -> Anime | None:
    return await session.scalar(
        select(Anime)
        .filter(Anime.slug == slug)
        .options(
            selectinload(Anime.companies).selectinload(CompanyAnime.company),
            selectinload(Anime.genres),
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
            Anime.franchise_id == anime.franchise_id
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
        .filter(Anime.franchise_id == anime.franchise_id)
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
        .filter(AnimeRecommendation.anime == anime)
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
        select(func.count(Company.id)).where(Company.slug.in_(slugs))
    )


async def anime_genre_count(session: AsyncSession, slugs: list[str]):
    return await session.scalar(
        select(func.count(AnimeGenre.id)).where(AnimeGenre.slug.in_(slugs))
    )


def anime_search_where(search: AnimeSearchArgs, query: Select):
    if search.years[0]:
        query = query.where(Anime.year >= search.years[0])

    if search.years[1]:
        query = query.where(Anime.year <= search.years[1])

    if search.score[0] and search.score[0] > 0:
        query = query.where(Anime.score >= search.score[0])

    if search.score[1]:
        query = query.where(Anime.score <= search.score[1])

    if len(search.season) > 0:
        query = query.where(Anime.season.in_(search.season))

    if len(search.rating) > 0:
        query = query.where(Anime.rating.in_(search.rating))

    if len(search.status) > 0:
        query = query.where(Anime.status.in_(search.status))

    if len(search.source) > 0:
        query = query.where(Anime.source.in_(search.source))

    if len(search.media_type) > 0:
        query = query.where(Anime.media_type.in_(search.media_type))

    if search.only_translated:
        query = query.filter(Anime.translated_ua == True)  # noqa: E712

    if len(search.producers) > 0:
        query = query.join(Anime.producers).filter(
            Company.slug.in_(search.producers)
        )

    if len(search.studios) > 0:
        query = query.join(Anime.studios).filter(
            Company.slug.in_(search.studios)
        )

    # All genres must be present in query result
    if len(search.genres) > 0:
        query = query.filter(
            and_(
                *[
                    Anime.genres.any(AnimeGenre.slug == slug)
                    for slug in search.genres
                ]
            )
        )

    return query


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

    query = select(Anime)
    query = anime_search_where(search, query)

    if len(search.sort) > 0:
        query = query.order_by(*utils.build_order_by(search.sort))

    query = query.options(*load_options)
    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def anime_search_total(session: AsyncSession, search: AnimeSearchArgs):
    query = select(func.count(Anime.id))
    query = anime_search_where(search, query)

    return await session.scalar(query)


async def anime_genres(session: AsyncSession):
    return await session.scalars(select(AnimeGenre).order_by(AnimeGenre.slug))


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

    query = select(Anime).where(Anime.slug.in_(slugs)).options(*load_options)

    if len(search.sort) > 0:
        query = query.order_by(*utils.build_order_by(search.sort))

    meilisearch_result["list"] = (await session.scalars(query)).unique().all()

    return meilisearch_result
