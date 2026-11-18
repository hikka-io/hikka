from meilisearch_python_sdk.models.settings import MeilisearchSettings
from app.utils import get_settings, to_timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app.models import Manga
from app import constants
from . import service


async def update_manga_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=[
                "translated_ua",
                "native_score",
                "media_type",
                "magazines",
                "mal_id",
                "genres",
                "status",
                "score",
                "year",
                "id",
            ],
            searchable_attributes=[
                "title_original",
                "title_native",
                "title_ua",
                "title_en",
                "synonyms",
                "mal_id",
            ],
            displayed_attributes=[
                "slug",
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


def manga_to_document(manga: Manga):
    magazines = []

    for magazine in manga.magazines:
        magazines.append(magazine.slug)

    return {
        "year": manga.start_date.year if manga.start_date else None,
        "genres": [genre.slug for genre in manga.genres],
        "start_date": to_timestamp(manga.start_date),
        "native_scored_by": manga.native_scored_by,
        "title_original": manga.title_original,
        "created": to_timestamp(manga.created),
        "updated": to_timestamp(manga.updated),
        "translated_ua": manga.translated_ua,
        "native_score": manga.native_score,
        "media_type": manga.media_type,
        "scored_by": manga.scored_by,
        "synonyms": manga.synonyms,
        "title_native": manga.title_native,
        "title_ua": manga.title_ua,
        "title_en": manga.title_en,
        "status": manga.status,
        "id": manga.content_id,
        "magazines": magazines,
        "mal_id": manga.mal_id,
        "score": manga.score,
        "slug": manga.slug,
    }


async def manga_documents(
    session: AsyncSession, limit: int, last_id: str | None
):
    query = (
        select(Manga)
        .filter(Manga.media_type != None)  # noqa: E711
        .filter(Manga.deleted == False)  # noqa: E712
        .filter(Manga.needs_search_update == True)  # noqa: E712
        .options(
            joinedload(Manga.magazines),
            joinedload(Manga.genres),
        )
    )

    return await service.get_documents(
        session, query, Manga.content_id, manga_to_document, limit, last_id
    )


async def manga_document_ids_delete(session: AsyncSession):
    query = (
        select(Manga)
        .filter(Manga.deleted == True)  # noqa: E712
        .filter(Manga.needs_search_update == True)  # noqa: E712
    )

    return await service.get_delete_ids(session, query, Manga.content_id)


async def update_search_manga():
    settings = get_settings()

    async with sessionmanager.session() as session:
        async with AsyncClient(**settings.meilisearch) as client:
            index = client.index(constants.SEARCH_INDEX_MANGA)

            await update_manga_settings(index)

            await service.index_documents(
                session, index, manga_documents, primary_key="id"
            )

            await service.delete_documents(
                session, index, manga_document_ids_delete
            )
