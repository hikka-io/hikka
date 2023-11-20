from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select, func
from app.utils import pagination
from app.models import Person
from app import constants
import math


async def update_people_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=["favorites"],
            searchable_attributes=[
                "name_native",
                "name_ua",
                "name_en",
            ],
            displayed_attributes=[
                "name_native",
                "name_ua",
                "name_en",
                "image",
                "slug",
            ],
            sortable_attributes=["favorites"],
            distinct_attribute="slug",
        )
    )


async def people_documents(session: AsyncSession, limit: int, offset: int):
    people_list = await session.scalars(
        select(Person).order_by("content_id").limit(limit).offset(offset)
    )

    documents = [
        {
            "name_native": person.name_native,
            "favorites": person.favorites,
            "name_ua": person.name_ua,
            "name_en": person.name_en,
            "id": person.content_id,
            "image": person.image,
            "slug": person.slug,
        }
        for person in people_list
    ]

    return documents


async def people_documents_total(session: AsyncSession):
    return await session.scalar(select(func.count(Person.id)))


async def meilisearch_populate(session: AsyncSession):
    print("Meilisearch: Populating people")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_PEOPLE)

        await update_people_settings(index)

        size = 1000
        total = await people_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            print(f"Meilisearch: Processing people page {page}")

            limit, offset = pagination(page, size)
            documents = await people_documents(session, limit, offset)

            await index.add_documents(documents)


async def update_search_people():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
