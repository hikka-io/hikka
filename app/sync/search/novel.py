from meilisearch_python_sdk.models.settings import MeilisearchSettings
from app.utils import get_settings, to_timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app.models import Novel
from app import constants
from . import service


async def update_novel_settings(index):
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


def novel_to_document(novel: Novel):
    magazines = []

    for magazine in novel.magazines:
        magazines.append(magazine.slug)

    return {
        "year": novel.start_date.year if novel.start_date else None,
        "genres": [genre.slug for genre in novel.genres],
        "start_date": to_timestamp(novel.start_date),
        "native_scored_by": novel.native_scored_by,
        "created": to_timestamp(novel.created),
        "updated": to_timestamp(novel.updated),
        "title_original": novel.title_original,
        "translated_ua": novel.translated_ua,
        "native_score": novel.native_score,
        "media_type": novel.media_type,
        "scored_by": novel.scored_by,
        "synonyms": novel.synonyms,
        "title_native": novel.title_native,
        "title_ua": novel.title_ua,
        "title_en": novel.title_en,
        "status": novel.status,
        "id": novel.content_id,
        "magazines": magazines,
        "mal_id": novel.mal_id,
        "score": novel.score,
        "slug": novel.slug,
    }


async def novel_documents(
    session: AsyncSession, limit: int, last_id: str | None
):
    query = (
        select(Novel)
        .filter(Novel.media_type != None)  # noqa: E711
        .filter(Novel.deleted == False)  # noqa: E712
        .filter(Novel.needs_search_update == True)  # noqa: E712
        .options(
            joinedload(Novel.magazines),
            joinedload(Novel.genres),
        )
    )

    return await service.get_documents(
        session, query, Novel.content_id, novel_to_document, limit, last_id
    )


async def novel_document_ids_delete(session: AsyncSession):
    query = (
        select(Novel)
        .filter(Novel.deleted == True)  # noqa: E712
        .filter(Novel.needs_search_update == True)  # noqa: E712
    )

    return await service.get_delete_ids(session, query, Novel.content_id)


async def update_search_novel():
    settings = get_settings()

    async with sessionmanager.session() as session:
        async with AsyncClient(**settings.meilisearch) as client:
            index = client.index(constants.SEARCH_INDEX_NOVEL)

            await update_novel_settings(index)

            await service.index_documents(
                session, index, novel_documents, primary_key="id"
            )

            await service.delete_documents(
                session, index, novel_document_ids_delete
            )
