from meilisearch_python_sdk.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_sdk import AsyncClient
from app.database import sessionmanager
from app.utils import get_settings
from app.models import Character
from sqlalchemy import select
from app import constants
from . import service


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
    query = select(Character).filter(
        Character.needs_search_update == True,  # noqa: E712
        Character.orphan == False,  # noqa: E712
    )

    return await service.get_documents(
        session,
        query,
        Character.content_id,
        character_to_document,
        limit,
        last_id,
    )


async def characters_document_ids_delete(session: AsyncSession):
    query = (
        select(Character)
        .filter(Character.orphan == True)  # noqa: E712
        .filter(Character.needs_search_update == True)  # noqa: E712
    )

    return await service.get_delete_ids(session, query, Character.content_id)


async def update_search_characters():
    settings = get_settings()

    async with sessionmanager.session() as session:
        async with AsyncClient(**settings.meilisearch) as client:
            index = client.index(constants.SEARCH_INDEX_CHARACTERS)

            await update_characters_settings(index)

            await service.index_documents(session, index, characters_documents)

            await service.delete_documents(
                session, index, characters_document_ids_delete
            )
