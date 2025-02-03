from meilisearch_python_sdk.models.settings import MeilisearchSettings
from meilisearch_python_sdk import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, func
from app.database import sessionmanager
from app.models import Collection
from app.utils import get_settings, to_timestamp, pagination
from app import constants
import math


async def update_collection_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            searchable_attributes=["title"],
            filterable_attributes=[
                "created",
                "system_ranking"
            ],
            displayed_attributes=[
                "visibility",
                "labels_order",
                "created",
                "updated",
                "content_type",
                "vote_score",
                "tags",
                "reference",
                "title",
                "description",

            ],
            sortable_attributes=[
                "created",
                "system_ranking"
            ],
            distinct_attribute="reference",
        )
    )


def collection_to_document(collection: Collection):
    return {
        "id": collection.reference,
        "created": to_timestamp(collection.created),
        "updated": to_timestamp(collection.updated),
        "title": collection.title,
        "reference": collection.reference,
        "content_type": collection.content_type,
        "system_ranking": collection.system_ranking,
        "description": collection.description if collection.description else None,
        "vote_score": collection.vote_score,
        "tags": [tag for tag in collection.tags],
        "labels_order": [label for label in collection.labels_order],
        "visibility": collection.visibility,

    }


async def collection_documents(session: AsyncSession, limit: int, offset: int):
    collections_list = await session.scalars(
        select(Collection)
        .filter(Collection.needs_search_update == True, Collection.deleted == False)  # noqa: E712
        .order_by(asc("created"))
        .limit(limit)
        .offset(offset)
    )

    documents = []

    for collection in collections_list:
        col_dict = collection_to_document(collection)
        documents.append(col_dict)
        collection.needs_search_update = False
        session.add(collection)

    return documents


async def collection_documents_total(session: AsyncSession):
    return await session.scalar(
        select(func.count(Collection.id))
        .filter(Collection.needs_search_update == True, Collection.deleted == False)
    )


async def meilisearch_populate(session: AsyncSession):
    print("Meilisearch: Populating collections")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_COLLECTION)

        await update_collection_settings(index)

        size = 1000
        total = await collection_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            print(f"Meilisearch: Processing collections page {page} of {pages}")

            limit, offset = pagination(page, size)
            documents = await collection_documents(session, limit, offset)
            print(f"Meilisearch: Processing collections documents size {len(documents)}")
            await index.add_documents(documents)

            # Let's just hope if Meilisearch is down this fails ;)
            await session.commit()


async def update_search_collections():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
