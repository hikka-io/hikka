from app.models import Company, CompanyAnime, Anime
from sqlalchemy.ext.asyncio import AsyncSession
from app.service import anime_loadonly
from sqlalchemy.orm import joinedload
from sqlalchemy import select, desc
from sqlalchemy import func
from app import constants


async def get_company_by_slug(
    session: AsyncSession, slug: str
) -> Company | None:
    return await session.scalar(
        select(Company).filter(func.lower(Company.slug) == slug.lower())
    )


async def search_total(session: AsyncSession, company_type: str | None):
    query = select(func.count(Company.id))

    if company_type == constants.COMPANY_ANIME_STUDIO:
        query = query.filter(Company.studio_anime.any())

    if company_type == constants.COMPANY_ANIME_PRODUCER:
        query = query.filter(Company.produced_anime.any())

    return await session.scalar(query)


async def companies_search(
    session: AsyncSession,
    company_type: str | None,
    limit: int,
    offset: int,
):
    query = select(Company)

    if company_type == constants.COMPANY_ANIME_STUDIO:
        query = query.filter(Company.studio_anime.any())

    if company_type == constants.COMPANY_ANIME_PRODUCER:
        query = query.filter(Company.produced_anime.any())

    return await session.scalars(
        query.order_by(
            desc(Company.favorites),
            desc(Company.content_id),
        )
        .limit(limit)
        .offset(offset)
    )


async def company_anime_total(
    session: AsyncSession, company: Company, company_type: str | None
):
    query = select(func.count(CompanyAnime.id)).filter(
        CompanyAnime.company == company
    )

    if company_type:
        query = query.filter(CompanyAnime.type == company_type)

    return await session.scalar(query)


async def company_anime(
    session: AsyncSession,
    company: Company,
    company_type: str | None,
    limit: int,
    offset: int,
):
    query = select(CompanyAnime).filter(CompanyAnime.company == company)

    if company_type:
        query = query.filter(CompanyAnime.type == company_type)

    return await session.scalars(
        query.join(Anime)
        .options(anime_loadonly(joinedload(CompanyAnime.anime)))
        .order_by(
            desc(Anime.score),
            desc(Anime.scored_by),
            desc(Anime.content_id),
        )
        .limit(limit)
        .offset(offset)
    )
