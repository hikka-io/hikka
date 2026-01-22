from meilisearch_python_sdk.models.settings import MeilisearchSettings
from app.utils import get_settings, to_timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from sqlalchemy.orm import joinedload
from sqlalchemy import select, func
from app.utils import pagination
from app.models import Manga
from app import constants
import math


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
        "title_ua": manga.title_ua,
        "title_en": manga.title_en,
        "status": manga.status,
        "id": manga.content_id,
        "magazines": magazines,
        "mal_id": manga.mal_id,
        "score": manga.score,
        "slug": manga.slug,
    }


async def manga_documents(session: AsyncSession, limit: int, offset: int):
    manga_list = await session.scalars(
        select(Manga)
        .filter(Manga.media_type != None)  # noqa: E711
        .filter(Manga.deleted == False)  # noqa: E712
        .filter(Manga.needs_search_update == True)  # noqa: E712
        .options(
            joinedload(Manga.magazines),
            joinedload(Manga.genres),
        )
        .order_by("content_id")
        .limit(limit)
        .offset(offset)
    )

    documents = []

    for manga in manga_list.unique().all():
        documents.append(manga_to_document(manga))

        # I'm not sure if this would behave correctly if Meilisearch is down
        manga.needs_search_update = False
        session.add(manga)

    return documents


async def manga_document_ids_delete(session: AsyncSession):
    manga_list = await session.scalars(
        select(Manga)
        .filter(Manga.deleted == True)  # noqa: E712
        .filter(Manga.needs_search_update == True)  # noqa: E712
    )

    delete_ids = []

    for manga in manga_list.unique().all():
        delete_ids.append(manga.content_id)
        manga.needs_search_update = False
        session.add(manga)

    return delete_ids


async def manga_documents_total(session: AsyncSession):
    return await session.scalar(
        select(func.count(Manga.id)).filter(
            Manga.needs_search_update == True  # noqa: E712
        )
    )


async def meilisearch_populate(session: AsyncSession):
    # print("Meilisearch: Populating manga")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_MANGA)

        await update_manga_settings(index)

        size = 1000
        total = await manga_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            # print(f"Meilisearch: Processing manga page {page} of {pages}")

            limit, offset = pagination(page, size)
            documents = await manga_documents(session, limit, offset)

            if len(documents) > 0:
                await index.add_documents(documents)

        delete_document_ids = await manga_document_ids_delete(session)

        if len(delete_document_ids) > 0:
            await index.delete_documents(delete_document_ids)
            # print(
            #     f"Meilisearch: deleted {len(delete_document_ids)} manga from search"
            # )

        # Let's just hope if Meilisearch is down this fails ;)
        await session.commit()


async def update_search_manga():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
