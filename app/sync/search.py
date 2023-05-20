from meilisearch_python_async.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_async import Client
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from app.utils import get_season
from sqlalchemy import select
from app.models import Anime
import config


async def update_anime_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=[
                "media_type",
                "producers",
                "episodes",
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
                "media_type",
                "scored_by",
                "title_ua",
                "title_en",
                "title_ja",
                "score",
                "slug",
                # ToDo: remove those
                "genres",
                "studios",
                "producers",
                "year",
            ],
            sortable_attributes=["scored_by", "score", "year"],
            distinct_attribute="slug",
        )
    )


async def anime_documents(session: AsyncSession):
    anime_list = await session.scalars(
        select(Anime)
        .where(Anime.media_type != None)
        .options(
            selectinload(Anime.producers),
            selectinload(Anime.studios),
            selectinload(Anime.genres),
        )
    )

    documents = [
        {
            "year": anime.start_date.year if anime.start_date else None,
            "producers": [company.slug for company in anime.producers],
            "studios": [company.slug for company in anime.studios],
            "genres": [genre.slug for genre in anime.genres],
            "season": get_season(anime.start_date),
            "media_type": anime.media_type,
            "scored_by": anime.scored_by,
            "synonyms": anime.synonyms,
            "episodes": anime.episodes,
            "title_ua": anime.title_ua,
            "title_en": anime.title_en,
            "title_ja": anime.title_ja,
            "status": anime.status,
            "source": anime.source,
            "rating": anime.rating,
            "id": anime.content_id,
            "score": anime.score,
            "slug": anime.slug,
        }
        for anime in anime_list
    ]

    return documents


async def meilisearch_populate(session: AsyncSession):
    print("Meilisearch: Populating database")

    # documents = await anime_documents(session)

    async with Client(**config.meilisearch) as client:
        index = client.index("content_anime")

        await update_anime_settings(index)

        # await index.add_documents(documents)


async def update_search():
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
