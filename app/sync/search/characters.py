from meilisearch_python_async.models.settings import MeilisearchSettings
from sqlalchemy.ext.asyncio import AsyncSession
from meilisearch_python_async import Client
from app.database import sessionmanager
from sqlalchemy import select, func
from app.models import Character
from app.utils import pagination
from app import constants
import config
import math


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


async def characters_documents(session: AsyncSession, limit: int, offset: int):
    characters_list = await session.scalars(
        select(Character).order_by("content_id").limit(limit).offset(offset)
    )

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


async def characters_documents_total(session: AsyncSession):
    return await session.scalar(select(func.count(Character.id)))


async def meilisearch_populate(session: AsyncSession):
    print("Meilisearch: Populating characters")

    async with Client(**config.meilisearch) as client:
        index = client.index(constants.SEARCH_INDEX_CHARACTERS)

        await update_characters_settings(index)

        size = 1000
        total = await characters_documents_total(session)
        pages = math.ceil(total / size)

        for page in range(1, pages + 1):
            print(f"Meilisearch: Processing characters page {page}")

            limit, offset = pagination(page, size)
            documents = await characters_documents(session, limit, offset)

            await index.add_documents(documents)


async def update_search_characters():
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        await meilisearch_populate(session)
