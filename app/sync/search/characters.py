from meilisearch_python_async.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_async import Client
from app.database import sessionmanager
from app.models import Character
from sqlalchemy import select
from app import constants
import config


async def update_characters_settings(index):
    await index.update_settings(
        MeilisearchSettings(
            filterable_attributes=["favorites"],
            searchable_attributes=[
                "name_ua",
                "name_en",
                "name_ja",
            ],
            displayed_attributes=[
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


async def characters_documents(session: AsyncSession):
    characters_list = await session.scalars(select(Character))

    documents = [
        {
            "favorites": character.favorites,
            "name_ua": character.name_ua,
            "name_en": character.name_en,
            "name_ja": character.name_ja,
            "id": character.content_id,
            "image": character.image,
            "slug": character.slug,
        }
        for character in characters_list
    ]

    return documents


async def meilisearch_populate(session: AsyncSession):
    print("Meilisearch: Populating characters")

    documents = await characters_documents(session)

    async with Client(**config.meilisearch) as client:
        index = client.index(constants.CHARACTERS_SEARCH_INDEX)

        await update_characters_settings(index)

        await index.add_documents(documents)


async def update_search_characters():
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
