from app.models import Anime, AnimeGenre, Company
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from sqlalchemy import select, func, and_
from .schemas import AnimeSearchArgs
from . import utils


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

    if len(search.season) > 0:
        query = query.where(
            Anime.season.in_(utils.enum_list_values(search.season))
        )

    if len(search.rating) > 0:
        query = query.where(
            Anime.rating.in_(utils.enum_list_values(search.rating))
        )

    if len(search.status) > 0:
        query = query.where(
            Anime.status.in_(utils.enum_list_values(search.status))
        )

    if len(search.source) > 0:
        query = query.where(
            Anime.source.in_(utils.enum_list_values(search.source))
        )

    if len(search.media_type) > 0:
        query = query.where(
            Anime.media_type.in_(utils.enum_list_values(search.media_type))
        )

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
    session: AsyncSession, search: AnimeSearchArgs, limit: int, offset: int
):
    query = select(Anime)
    query = anime_search_where(search, query)

    if len(search.sort) > 0:
        query = query.order_by(*utils.build_order_by(search.sort))

    query = query.limit(limit).offset(offset)

    return await session.scalars(query)


async def anime_search_total(session: AsyncSession, search: AnimeSearchArgs):
    query = select(func.count(Anime.id))
    query = anime_search_where(search, query)

    return await session.scalar(query)
