from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from app.models import Character
from sqlalchemy import select
from app import constants


async def update_characters_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=["favorites"],
            searchable_attributes=[
                "synonyms",
                "name_ua",
                "name_en",
                "name_ja",
            ],
            displayed_attributes=[
                "data_type",
                "synonyms",
                "name_ua",
                "name_en",
                "name_ja",
                "image",
                "slug",
            ],
            sortable_attributes=["favorites"],
            distinct_attribute="slug",
        )
    )


def character_to_document(character: Character):
    return {
        "data_type": "character",
        "favorites": character.favorites,
        "synonyms": character.synonyms,
        "name_ua": character.name_ua,
        "name_en": character.name_en,
        "name_ja": character.name_ja,
        "id": character.content_id,
        "image": character.image,
        "slug": character.slug,
    }


async def characters_documents(
    session: AsyncSession, limit: int, last_id: str | None
):
    query = (
        select(Character)
        .filter(
            Character.needs_search_update == True,  # noqa: E712
            Character.orphan == False,  # noqa: E712
        )
        .order_by(Character.content_id)
        .limit(limit)
    )

    # Rows drop out of the filter once indexed so we page by key
    if last_id:
        query = query.filter(Character.content_id > last_id)

    characters_list = await session.scalars(query)

    documents = []

    for character in characters_list:
        documents.append(character_to_document(character))
        last_id = character.content_id
        character.needs_search_update = False
        session.add(character)

    return documents, last_id


async def characters_document_ids_delete(session: AsyncSession):
    characters_list = await session.scalars(
        select(Character)
        .filter(Character.orphan == True)  # noqa: E712
        .filter(Character.needs_search_update == True)  # noqa: E712
    )

    delete_ids = []

    for character in characters_list:
        delete_ids.append(character.content_id)
        character.needs_search_update = False
        session.add(character)

    return delete_ids


async def meilisearch_populate(session: AsyncSession):
    # print("Meilisearch: Populating characters")

    settings = get_settings()

    async with AsyncClient(**settings.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_CHARACTERS)

        await update_characters_settings(index)

        size = 1000
        last_id = None

        while True:
            documents, last_id = await characters_documents(
                session, size, last_id
            )

            if len(documents) == 0:
                break

            await index.add_documents(documents)

        delete_document_ids = await characters_document_ids_delete(session)

        if len(delete_document_ids) > 0:
            await index.delete_documents(delete_document_ids)
            print(
                f"Meilisearch: deleted {len(delete_document_ids)} characters from search"
            )

        await session.commit()


async def update_search_characters():
    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
