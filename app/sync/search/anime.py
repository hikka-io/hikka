from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.utils import get_season, pagination
from app.models import Anime, CompanyAnime
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from app.settings import get_settings
from sqlalchemy import select, func
from app import constants
import math


async def update_anime_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=[
                "episodes_released",
                "episodes_total",
                "media_type",
                "producers",
                "studios",
                "rating",
                "season",
                "genres",
                "status",
                "source",
                "score",
                "year",
            ],
            searchable_attributes=[
                "title_ua",
                "title_en",
                "title_ja",
                "synonyms",
            ],
            displayed_attributes=[
                "episodes_released",
                "episodes_total",
                "media_type",
                "scored_by",
                "title_ua",
                "title_en",
                "title_ja",
                "poster",
                "status",
                "season",
                "source",
                "rating",
                "score",
                "slug",
                "year",
            ],
            sortable_attributes=["scored_by", "score", "year"],
            distinct_attribute="slug",
        )
    )


async def anime_documents(session: AsyncSession, limit: int, offset: int):
    anime_list = await session.scalars(
        select(Anime)
        .where(Anime.media_type is not None)
        .options(
            selectinload(Anime.companies).selectinload(CompanyAnime.company),
            selectinload(Anime.genres),
        )
        .order_by("content_id")
        .limit(limit)
        .offset(offset)
    )

    documents = []

    for anime in anime_list:
        producers = []
        studios = []

        for company_anime in anime.companies:
            if company_anime.type == constants.COMPANY_ANIME_PRODUCER:
                producers.append(company_anime.company.slug)

            if company_anime.type == constants.COMPANY_ANIME_STUDIO:
                studios.append(company_anime.company.slug)

        documents.append(
            {
                "year": anime.start_date.year if anime.start_date else None,
                "genres": [genre.slug for genre in anime.genres],
                "episodes_released": anime.episodes_released,
                "episodes_total": anime.episodes_total,
                "season": get_season(anime.start_date),
                "media_type": anime.media_type,
                "scored_by": anime.scored_by,
                "synonyms": anime.synonyms,
                "title_ua": anime.title_ua,
                "title_en": anime.title_en,
                "title_ja": anime.title_ja,
                "poster": anime.poster,
                "status": anime.status,
                "source": anime.source,
                "rating": anime.rating,
                "id": anime.content_id,
                "producers": producers,
                "score": anime.score,
                "studios": studios,
                "slug": anime.slug,
            }
        )

    return documents


async def anime_documents_total(session: AsyncSession):
    return await session.scalar(select(func.count(Anime.id)))


async def meilisearch_populate(session: AsyncSession):
    print("Meilisearch: Populating anime")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_ANIME)

        await update_anime_settings(index)

        size = 1000
        total = await anime_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            print(f"Meilisearch: Processing anime page {page}")

            limit, offset = pagination(page, size)
            documents = await anime_documents(session, limit, offset)

            await index.add_documents(documents)


async def update_search_anime():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
