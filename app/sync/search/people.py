from meilisearch_python_async.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_async import Client
from app.database import sessionmanager
from app.models import Person
from sqlalchemy import select
from app import constants
import config


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


async def people_documents(session: AsyncSession):
    people_list = await session.scalars(select(Person))

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


async def meilisearch_populate(session: AsyncSession):
    print("Meilisearch: Populating people")

    documents = await people_documents(session)

    async with Client(**config.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_PEOPLE)

        await update_people_settings(index)

        await index.add_documents(documents)


async def update_search_people():
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
