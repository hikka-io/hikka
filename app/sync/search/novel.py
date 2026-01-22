from meilisearch_python_sdk.models.settings import MeilisearchSettings
from app.utils import get_settings, to_timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func
from app.utils import pagination
from app.models import Novel
from app import constants
import math


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
            ],
            searchable_attributes=[
                "title_original",
                "title_ua",
                "title_en",
                "synonyms",
                "mal_id",
            ],
            displayed_attributes=[
                "slug",
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
        "title_ua": novel.title_ua,
        "title_en": novel.title_en,
        "status": novel.status,
        "id": novel.content_id,
        "magazines": magazines,
        "mal_id": novel.mal_id,
        "score": novel.score,
        "slug": novel.slug,
    }


async def novel_documents(session: AsyncSession, limit: int, offset: int):
    novel_list = await session.scalars(
        select(Novel)
        .filter(Novel.media_type != None)  # noqa: E711
        .filter(Novel.deleted == False)  # noqa: E712
        .filter(Novel.needs_search_update == True)  # noqa: E712
        .options(
            joinedload(Novel.magazines),
            joinedload(Novel.genres),
        )
        .order_by("content_id")
        .limit(limit)
        .offset(offset)
    )

    documents = []

    for novel in novel_list.unique().all():
        documents.append(novel_to_document(novel))

        # I'm not sure if this would behave correctly if Meilisearch is down
        novel.needs_search_update = False
        session.add(novel)

    return documents


async def novel_document_ids_delete(session: AsyncSession):
    novel_list = await session.scalars(
        select(Novel)
        .filter(Novel.deleted == True)  # noqa: E712
        .filter(Novel.needs_search_update == True)  # noqa: E712
    )

    delete_ids = []

    for novel in novel_list.unique().all():
        delete_ids.append(novel.content_id)
        novel.needs_search_update = False
        session.add(novel)

    return delete_ids


async def novel_documents_total(session: AsyncSession):
    return await session.scalar(
        select(func.count(Novel.id)).filter(
            Novel.needs_search_update == True  # noqa: E712
        )
    )


async def meilisearch_populate(session: AsyncSession):
    # print("Meilisearch: Populating novel")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_NOVEL)

        await update_novel_settings(index)

        size = 1000
        total = await novel_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            # print(f"Meilisearch: Processing novel page {page} of {pages}")

            limit, offset = pagination(page, size)
            documents = await novel_documents(session, limit, offset)

            if len(documents) > 0:
                await index.add_documents(documents)

        delete_document_ids = await novel_document_ids_delete(session)

        if len(delete_document_ids) > 0:
            await index.delete_documents(delete_document_ids)
            # print(
            #     f"Meilisearch: deleted {len(delete_document_ids)} novel from search"
            # )

        # Let's just hope if Meilisearch is down this fails ;)
        await session.commit()


async def update_search_novel():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
