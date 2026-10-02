from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from sqlalchemy import select, asc, func, or_
from app.database import sessionmanager
from app.utils import get_settings
from app.models import Collection
from app import constants
import math


async def update_collections_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=["content_type", "tags"],
            searchable_attributes=["title", "tags"],
            displayed_attributes=["content_type", "title", "tags", "id"],
        )
    )


def collection_to_document(collection: Collection):
    return {
        "content_type": collection.content_type,
        "id": collection.reference,
        "title": collection.title,
        "tags": collection.tags,
    }


async def collections_documents(session: AsyncSession, limit: int):
    # NOTE: no offset here on purpose - autoflush writes needs_search_update
    # back before the next query runs, so each batch starts from the top
    collections_list = await session.scalars(
        select(Collection)
        .filter(
            Collection.visibility == constants.COLLECTION_PUBLIC,
            Collection.needs_search_update == True,  # noqa: E712
            Collection.deleted == False,  # noqa: E712
        )
        .order_by(asc(Collection.created))
        .limit(limit)
    )

    documents = []

    for collection in collections_list:
        documents.append(collection_to_document(collection))
        collection.needs_search_update = False
        session.add(collection)

    return documents


async def collections_documents_total(session: AsyncSession):
    return await session.scalar(
        select(func.count(Collection.id)).filter(
            Collection.visibility == constants.COLLECTION_PUBLIC,
            Collection.needs_search_update == True,  # noqa: E712
            Collection.deleted == False,  # noqa: E712
        )
    )


async def collections_document_ids_delete(session: AsyncSession):
    # Collections that are no longer public must be dropped from the index
    collections_list = await session.scalars(
        select(Collection).filter(
            Collection.needs_search_update == True,  # noqa: E712
            or_(
                Collection.visibility != constants.COLLECTION_PUBLIC,
                Collection.deleted == True,  # noqa: E712
            ),
        )
    )

    delete_ids = []

    for collection in collections_list:
        delete_ids.append(collection.reference)
        collection.needs_search_update = False
        session.add(collection)

    return delete_ids


async def meilisearch_populate(session: AsyncSession):
    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_COLLECTIONS)

        await update_collections_settings(index)

        size = 1000
        total = await collections_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            documents = await collections_documents(session, size)

            if len(documents) > 0:
                await index.add_documents(documents, primary_key="id")

        delete_document_ids = await collections_document_ids_delete(session)

        if len(delete_document_ids) > 0:
            await index.delete_documents(delete_document_ids)

        # Let's just hope if Meilisearch is down this fails ;)
        await session.commit()


async def update_search_collections():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
