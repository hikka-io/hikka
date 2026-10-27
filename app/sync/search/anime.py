from meilisearch_python_sdk.models.settings import MeilisearchSettings
from app.utils import get_settings, to_timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.models import Anime, CompanyAnime
from sqlalchemy.orm import selectinload
from app.database import sessionmanager
from app.utils import get_season
from sqlalchemy import select
from app import constants


async def update_anime_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=[
                "episodes_released",
                "episodes_total",
                "airing_seasons",
                "translated_ua",
                "native_score",
                "media_type",
                "producers",
                "studios",
                "rating",
                "season",
                "genres",
                "status",
                "source",
                "mal_id",
                "score",
                "year",
                "id",
            ],
            searchable_attributes=[
                "title_native",
                "title_ua",
                "title_en",
                "title_ja",
                "synonyms",
                "mal_id",
            ],
            displayed_attributes=[
                "episodes_released",
                "native_scored_by",
                "episodes_total",
                "translated_ua",
                "native_score",
                "media_type",
                "scored_by",
                "title_ua",
                "title_en",
                "title_ja",
                "status",
                "season",
                "source",
                "rating",
                "score",
                "slug",
                "year",
                "id",
            ],
            sortable_attributes=[
                "native_scored_by",
                "native_score",
                "media_type",
                "start_date",
                "scored_by",
                "created",
                "updated",
                "score",
                "year",
            ],
            distinct_attribute="slug",
            ranking_rules=[
                "words",
                "typo",
                "proximity",
                "attribute",
                "sort",
                "exactness",
            ],
        )
    )


def anime_to_document(anime: Anime):
    producers = []
    studios = []

    for company_anime in anime.companies:
        if company_anime.type == constants.COMPANY_ANIME_PRODUCER:
            producers.append(company_anime.company.slug)

        if company_anime.type == constants.COMPANY_ANIME_STUDIO:
            studios.append(company_anime.company.slug)

    return {
        "year": anime.start_date.year if anime.start_date else None,
        "genres": [genre.slug for genre in anime.genres],
        "start_date": to_timestamp(anime.start_date),
        "episodes_released": anime.episodes_released,
        "native_scored_by": anime.native_scored_by,
        "episodes_total": anime.episodes_total,
        "airing_seasons": anime.airing_seasons,
        "created": to_timestamp(anime.created),
        "updated": to_timestamp(anime.updated),
        "season": get_season(anime.start_date),
        "translated_ua": anime.translated_ua,
        "native_score": anime.native_score,
        "media_type": anime.media_type,
        "scored_by": anime.scored_by,
        "synonyms": anime.synonyms,
        "title_native": anime.title_native,
        "title_ua": anime.title_ua,
        "title_en": anime.title_en,
        "title_ja": anime.title_ja,
        "status": anime.status,
        "source": anime.source,
        "rating": anime.rating,
        "id": anime.content_id,
        "producers": producers,
        "mal_id": anime.mal_id,
        "score": anime.score,
        "slug": anime.slug,
        "studios": studios,
    }


async def anime_documents(
    session: AsyncSession, limit: int, last_id: str | None
):
    # Rows stay locked until the batch is committed so edits made
    # meanwhile wait and flag the row again instead of being overwritten
    query = (
        select(Anime)
        .filter(Anime.deleted == False)  # noqa: E712
        .filter(Anime.needs_search_update == True)  # noqa: E712
        .options(
            selectinload(Anime.companies).selectinload(CompanyAnime.company),
            selectinload(Anime.genres),
        )
        .order_by(Anime.content_id)
        .limit(limit)
        .with_for_update(of=Anime, skip_locked=True)
    )

    # Rows drop out of the filter once indexed so we page by key
    if last_id:
        query = query.filter(Anime.content_id > last_id)

    anime_list = await session.scalars(query)

    documents = []

    for anime in anime_list:
        documents.append(anime_to_document(anime))
        last_id = anime.content_id

        # I'm not sure if this would behave correctly if Meilisearch is down
        anime.needs_search_update = False
        session.add(anime)

    return documents, last_id


async def anime_document_ids_delete(session: AsyncSession):
    anime_list = await session.scalars(
        select(Anime)
        .filter(Anime.deleted == True)  # noqa: E712
        .filter(Anime.needs_search_update == True)  # noqa: E712
        .with_for_update(of=Anime, skip_locked=True)
    )

    delete_ids = []

    for anime in anime_list:
        delete_ids.append(anime.content_id)
        anime.needs_search_update = False
        session.add(anime)

    return delete_ids


async def meilisearch_populate(session: AsyncSession):
    # print("Meilisearch: Populating anime")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_ANIME)

        await update_anime_settings(index)

        size = 1000
        last_id = None

        while True:
            documents, last_id = await anime_documents(session, size, last_id)

            if len(documents) == 0:
                break

            await index.add_documents(documents, primary_key="id")

            # Commit each batch so row locks are released right away
            await session.commit()

        delete_document_ids = await anime_document_ids_delete(session)

        if len(delete_document_ids) > 0:
            await index.delete_documents(delete_document_ids)
            print(
                f"Meilisearch: deleted {len(delete_document_ids)} animes from search"
            )

        # Let's just hope if Meilisearch is down this fails ;)
        await session.commit()


async def update_search_anime():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
