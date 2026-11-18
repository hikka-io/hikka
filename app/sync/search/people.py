from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from sqlalchemy import select
from app.models import Person
from app import constants
from . import service


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
        select(Person).filter(Person.needs_search_update == True)  # noqa: E712
    )

    return await service.get_documents(
        session, query, Person.content_id, person_to_document, limit, last_id
    )


async def update_search_people():
    settings = get_settings()

    async with sessionmanager.session() as session:
        async with AsyncClient(**settings.meilisearch) as client:
            index = client.index(constants.SEARCH_INDEX_PEOPLE)

            await update_people_settings(index)

            await service.index_documents(session, index, people_documents)
