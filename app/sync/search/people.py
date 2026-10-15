from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import Person
from app import constants


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


async def people_documents(
    session: AsyncSession, limit: int, last_id: str | None
):
    query = (
        select(Person)
        .filter(Person.needs_search_update == True)  # noqa: E712
        .order_by(Person.content_id)
        .limit(limit)
    )

    # Rows drop out of the filter once indexed so we page by key
    if last_id:
        query = query.filter(Person.content_id > last_id)

    people_list = await session.scalars(query)

    documents = []

    for person in people_list:
        documents.append(person_to_document(person))
        last_id = person.content_id
        person.needs_search_update = False
        session.add(person)

    return documents, last_id


async def meilisearch_populate(session: AsyncSession):
    # print("Meilisearch: Populating people")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_PEOPLE)

        await update_people_settings(index)

        size = 1000
        last_id = None

        while True:
            documents, last_id = await people_documents(session, size, last_id)

            if len(documents) == 0:
                break

            await index.add_documents(documents)

            await session.commit()


async def update_search_people():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
