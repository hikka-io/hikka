from meilisearch_python_sdk.models.settings import MeilisearchSettings
from app.utils import get_settings, to_timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from sqlalchemy.orm import joinedload
from sqlalchemy import select, asc, func
from app.database import sessionmanager
from app.models import Collection
from app.utils import pagination
from app import constants
import math


async def update_collection_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            searchable_attributes=["title"],
            displayed_attributes=["id", "title"],
            sortable_attributes=["title"],
            distinct_attribute="id",
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


def collection_to_document(collection: Collection):
    return {
        "title": collection.title,
        "id": str(collection.id),
    }


async def collection_documents(
    session: AsyncSession, limit: int, offset: int
):
    collections = await session.scalars(
        select(Collection)
        .filter(Collection.needs_search_update == True)  # noqa: E712
        .options(joinedload(Collection.author))
        .order_by(asc(Collection.created))
        .limit(limit)
        .offset(offset)
    )

    upsert = []
    delete_ids = []

    for collection in collections:
        is_public = collection.visibility == constants.COLLECTION_PUBLIC

        if not collection.deleted and is_public:
            upsert.append(collection_to_document(collection))
        else:
            delete_ids.append(str(collection.id))

        collection.needs_search_update = False
        session.add(collection)

    return upsert, delete_ids


async def collection_documents_total(session: AsyncSession):
    return await session.scalar(
        select(func.count(Collection.id)).filter(
            Collection.needs_search_update == True  # noqa: E712
        )
    )


async def meilisearch_populate(session: AsyncSession):
    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_COLLECTIONS)

        await update_collection_settings(index)

        size = 1000
        total = await collection_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            limit, offset = pagination(page, size)
            upsert, delete_ids = await collection_documents(
                session, 
                limit, 
                offset
            )

            if upsert:
                await index.add_documents(upsert)

            if delete_ids:
                await index.delete_documents(delete_ids)

            await session.commit()


async def update_search_collections():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
