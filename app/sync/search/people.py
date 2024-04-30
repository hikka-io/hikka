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
                "synonyms",
                "name_ua",
                "name_en",
            ],
            displayed_attributes=[
                "data_type",
                "description_ua",
                "name_native",
                "synonyms",
                "name_ua",
                "name_en",
                "image",
                "slug",
            ],
            sortable_attributes=["favorites"],
            distinct_attribute="slug",
        )
    )


def person_to_document(person: Person):
    return {
        "data_type": "person",
        "description_ua": person.description_ua,
        "name_native": person.name_native,
        "favorites": person.favorites,
        "synonyms": person.synonyms,
        "name_ua": person.name_ua,
        "name_en": person.name_en,
        "id": person.content_id,
        "image": person.image,
        "slug": person.slug,
    }


async def people_documents(session: AsyncSession, limit: int, offset: int):
    people_list = await session.scalars(
        select(Person)
        .filter(Person.needs_search_update == True)  # noqa: E712
        .order_by("content_id")
        .limit(limit)
        .offset(offset)
    )

    documents = []

    for person in people_list:
        documents.append(person_to_document(person))
        person.needs_search_update = False
        session.add(person)

    return documents


async def people_documents_total(session: AsyncSession):
    return await session.scalar(
        select(func.count(Person.id)).filter(
            Person.needs_search_update == True  # noqa: E712
        )
    )


async def meilisearch_populate(session: AsyncSession):
    # print("Meilisearch: Populating people")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_PEOPLE)

        await update_people_settings(index)

        size = 1000
        total = await people_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            # print(f"Meilisearch: Processing people page {page} of {pages}")

            limit, offset = pagination(page, size)
            documents = await people_documents(session, limit, offset)

            await index.add_documents(documents)

            await session.commit()


async def update_search_people():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
